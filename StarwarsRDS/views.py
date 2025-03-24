from django.http import HttpResponse
from django.shortcuts import render, redirect
from os import getenv


from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable

store = SPARQLStore("http://graphdb:7200/repositories/starwars", context_aware=False, returnFormat='json',
                    method='GET')
graph = Graph(store)


def home(request):  # TODO: add an actual home page
    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(graph)})

def handle_404_error(request,exception):
    return render(request,'error404.html')

def search(request):
    q = request.GET.get('q','')

    if is_valid_uri(q):
        #if it's a valid uri (and not a simple search string), then there's a high likelihood that it's an existing page so look for it
        query=f"""
            ASK {{
                <{q}> ?p ?o 
            }}
        """
        try:
            if graph.query(query):
                return redirect(q)
        except Exception as e:
            pass

    #since it's not a subject, then it's likely either a literal or a user-defined string, so check for objects (also, since we have search bar, it might also be a partial string)
    query=f"""
    SELECT DISTINCT ?s ?sName ?p
    WHERE {{
        ?s ?p ?o .
        FILTER (regex(?o,"{q}","i"))
        ?s rdfs:label ?sName .
    }} UNION {{
       ?s ?p ?o .
       FILTER(?p=rdf:type)
       FILTER(?p={q})
       ?s rdfs:label ?sName .
    }}
    """

    results=graph.query(query)

    if len(results)==1:
        result=next(iter(results))
        return redirect(result.s) #if only one result we can iterate
    else:
        results_list=[] #else just show all (if any results)
        for result in results:
            results_list.append({
                "uri": result.s,
                "name": result.sName,
                "relation":to_human_readable(result.p)
            })
        return render(request, 'search.html', {'results':results_list, 'query_string':q})

