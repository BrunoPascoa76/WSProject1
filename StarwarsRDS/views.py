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

    results = graph.query(query,initBindings={'q':URIRef(q) if is_valid_uri(q) else Literal(q)})

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

def character_details(request,_name):
    match request.method:
        case 'GET':
            details=defaultdict(list)

            uri=request.build_absolute_uri()
            query = """
            SELECT DISTINCT ?p ?o ?sName
            WHERE {
                ?uri ?p ?o .
                OPTIONAL { ?o rdfs:label ?sName }
            }
            """

            result=graph.query(query,initBindings={'uri':URIRef(uri)})

            for p, o, oName in result:
                p_human_readable = to_human_readable(p)
                if oName: #while I talk about them generically here, you can use them by name on the template
                    details[p_human_readable].append((str(o),str(oName)))
                else:
                    details[p_human_readable].append(str(o))

            return render(request,"character_details.html", {"character": details})


        #os outros faço depois de teres o form