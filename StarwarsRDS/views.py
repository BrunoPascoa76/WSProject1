import re
from collections import defaultdict
from unittest import case
from os import getenv

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from os import getenv
from rdflib.plugins.sparql import prepareQuery, prepareUpdate
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote
from .forms import CharacterAttributesForm, CharacterRelationsForm
import json
from urllib.parse import unquote

from rdflib import Graph, URIRef, Literal, RDFS, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable, get_details

endpoint = "http://localhost:7200/"

store = SPARQLUpdateStore("http://localhost:7200/repositories/starwars", context_aware=False, returnFormat='')
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

def type_graph(request,_type):
    query="""
    CONSTRUCT {
        ?s rdf:type ?type ;
               ?p ?o .
    }WHERE{
        ?s rdf:type ?type ;
            ?p ?o .
    }
    """
    uri=request.build_absolute_uri()[:-1] #to remove the last "/"
    local_graph=graph.query(query,initBindings={'type':URIRef(uri)}).graph
    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(local_graph)})


details_query="""
SELECT ?p ?o ?oName
WHERE{
    ?uri ?p ?o .
    OPTIONAL { ?o rdfs:label ?oName . }
}
"""


def character_details(request,_id):
    details=get_details(request)

    return render(request,'character_details.html',{'character':details})


def city_details(request, _id):
    details=get_details(request)

    return render(request, 'city_details.html', {'character': details})