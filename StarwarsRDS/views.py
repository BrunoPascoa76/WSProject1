import re
from collections import defaultdict
from unittest import case
from os import getenv

from django.http import HttpResponse
from django.shortcuts import render, redirect
from os import getenv
from rdflib.plugins.sparql import prepareQuery, prepareUpdate

from rdflib import Graph, URIRef, Literal, RDFS, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable

store = SPARQLUpdateStore(getenv("GRAPHDB_URL"), getenv("GRAPHDB_UPDATE_URL"), context_aware=False, returnFormat='json')
graph = Graph(store)


def home(request):
    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(graph)})


def handle_404_error(request, exception):
    return render(request, 'error404.html')


def search(request):
    q = request.GET.get('q', '')

    if is_valid_uri(q):
        # q is either a subject or is a type (the only relevant uri that is object only, at least for now)
        query = """
        SELECT DISTINCT ?s ?p ?o ?sName
        WHERE {
            ?s ?p ?o .
            FILTER((?s = ?q && ?p = rdfs:label) || (?p = rdf:type && ?o = ?q))
            ?s rdfs:label ?sName .
        }
        """
    else:
        # search for instances where it is an object (or part of it)
        query ="""
            SELECT DISTINCT ?s ?sName ?p
            WHERE {
                ?s ?p ?o .
                FILTER (regex(?o,?q,"i"))
                ?s rdfs:label ?sName .
            }
        """

    results = graph.query(str(query),initBindings={'q':URIRef(q) if is_valid_uri(q) else Literal(q)})

    if len(results) == 1:
        result = next(iter(results))
        return redirect(result.s)  # if only one result we can just redirect
    else:
        results_list = []  # else just show all (if any results)
        for result in results:
            results_list.append({
                "uri": result.s,
                "name": result.sName,
                "relation": to_human_readable(result.p)
            })
        return render(request, 'search.html', {'results': results_list, 'query_string': re.split(r'[/#]', q)[-1]})


def description(request, _type, _name):
    match request.method:
        case 'GET':
            return get_description(request)
        case 'POST':
            return add_description(request)
        case 'PUT':
            return update_description(request)
        case 'DELETE':
            return delete_description(request)


def get_description(request):
    uri = request.build_absolute_uri()
    attributes = defaultdict(list)
    relations = defaultdict(list)

    # will need to divide between triples where the object is a literal ("attributes") and ones where the objects is a URI ("relations") for later (because on update, I need to know whether  I need to add the type for consistency's sake
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        attributes[p_human_readable].append(o)

    relations_query = """
        SELECT DISTINCT ?p ?o ?oName
        WHERE {
            ?uri ?p ?o .
            ?o rdfs:label ?oName .
        }
    """

    for p, o, oName in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        relations[p_human_readable].append((o, oName))

    return render(request, 'description.html',
                  {'label': attributes["label"][0], 'attributes': attributes, 'relations': relations})


def add_description(request):
    pass


def update_description(request):
    pass


def delete_description(request):
    pass
