from django.shortcuts import render
from os import getenv

from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from .utils import rdflib_graph_to_html

store = SPARQLStore("http://graphdb:7200/repositories/starwars", context_aware=False, returnFormat='json',
                    method='GET')
graph = Graph(store)


def home(request):  # TODO: add an actual home page
    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(graph)})

def handle_404_error(request,exception):
    return render(request,'error404.html')