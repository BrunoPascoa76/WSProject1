import re

from django.http import HttpResponse
from django.shortcuts import render, redirect
from os import getenv


from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable

store = SPARQLStore("http://graphdb:7200/repositories/starwars", context_aware=False, returnFormat='json',
                    method='GET')
graph = Graph(store)


def home(request):
    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(graph)})

def handle_404_error(request,exception):
    return render(request,'error404.html')

def search(request):
    q = request.GET.get('q','')

    if is_valid_uri(q):
        #q is either a subject or is a type (the only relevant uri that is object only, at least for now)
        query=f"""
        SELECT DISTINCT ?s ?p ?o ?sName
        WHERE {{
            ?s ?p ?o .
            FILTER((?s=<{q}> && ?p=rdfs:label) || (?p=rdf:type && ?o=<{q}>))
            ?s rdfs:label ?sName .
        }}
        """
    else:
        #search for instances where it is an object (or part of it)
        query=f"""
            SELECT DISTINCT ?s ?sName ?p
            WHERE {{
                ?s ?p ?o .
                FILTER (regex(?o,"{q}","i"))
                ?s rdfs:label ?sName .
            }}
        """

    results=graph.query(query)

    if len(results)==1:
        result=next(iter(results))
        return redirect(result.s) #if only one result we can just redirect
    else:
        results_list=[] #else just show all (if any results)
        for result in results:
            results_list.append({
                "uri": result.s,
                "name": result.sName,
                "relation":to_human_readable(result.p)
            })
        return render(request, 'search.html', {'results':results_list, 'query_string':re.split(r'[/#]',q)[-1]})

