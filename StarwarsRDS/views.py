import re
from collections import defaultdict
from unittest import case
from os import getenv

from django.http import HttpResponse, JsonResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from os import getenv
from rdflib.plugins.sparql import prepareQuery, prepareUpdate
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote

from . import queries
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from urllib.parse import unquote

from rdflib import Graph, URIRef, Literal, RDFS, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
import os

from .forms import CharacterForm
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable, get_details, get_list, update_character, \
    remove_entity

endpoint = "http://graphdb:7200/"
repo_name = "starwars"

client = ApiClient(endpoint=endpoint)

accessor = GraphDBApi(client)

store = SPARQLUpdateStore(getenv("GRAPHDB_URL"), getenv("GRAPHDB_UPDATE_URL"), context_aware=False)
graph = Graph(store)


def home(request):
    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(graph)})


def handle_404_error(request, exception):
    return render(request, 'error404.html')


def search(request):
    q = request.GET.get('q', '')

    if is_valid_uri(q):
        # q is either a subject or is a type (the only relevant uri that is object only, at least for now)
        query = queries.SEARCH_SUBJECT
    else:
        # search for instances where it is an object (or part of it)
        query =queries.SEARCH_OBJECT

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


def character_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request,'character_details.html',{'character':details})

def city_details(request, _id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'city_details.html', {'city': details})

def droid_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'droid_details.html', {'droid': details})

def film_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'film_details.html', {'film': details})

def music_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'music_details.html', {'music': details})

def organization_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'organization_details.html', {'organization': details})

def planet_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'planet_details.html', {'planet': details})

def quote_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request, 'quote_details.html', {'quote': details})

def specie_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request,"species_details.html",{'specie': details})

def starship_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request,"starship_details.html",{'starship': details})

def vehicle_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request,"vehicle_details.html",{'vehicle': details})

def weapon_details(request,_id):
    details=get_details(request.build_absolute_uri(),graph)
    return render(request,"weapon_details.html",{'weapon':details})


def characters(request):
    uri="http://localhost:8000/Character"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'characters.html',{"characters":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def cities(request):
    uri="http://localhost:8000/City"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'cities.html',{"cities":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def droids(request):
    uri="http://localhost:8000/Droid"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'droids.html',{"droids":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def films(request):
    uri="http://localhost:8000/Film"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'films.html',{"films":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def music(request):
    uri="http://localhost:8000/Music"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'music.html',{"music":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def organizations(request):
    uri="http://localhost:8000/Organization"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'organizations.html',{"organizations":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def planets(request):
    uri="http://localhost:8000/Planet"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'planets.html',{"planets":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def quotes(request):
    uri="http://localhost:8000/Quote"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'quotes.html',{"quotes":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def species(request):
    uri="http://localhost:8000/Specie"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'species.html',{"species":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def starships(request):
    uri="http://localhost:8000/Starship"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'starships.html',{"starships":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def vehicles(request):
    uri="http://localhost:8000/Vehicle"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'vehicles.html',{"vehicles":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})

def weapons(request):
    uri="http://localhost:8000/Weapon"
    query = queries.CONSTRUCT_LOCAL_GRAPH
    local_graph = graph.query(query, initBindings={'type': URIRef(uri)}).graph
    return render(request,'weapons.html',{"weapons":get_list(uri,graph),"graph_html": rdflib_graph_to_html(local_graph)})


def edit_character(request,_id=None):
    if request.method == "GET":
        if _id: #the id itself is not important, it's just that I needed it for the path (and now use it to decide whether it's an updade or insert
            character_uri=request.build_absolute_uri().split("/")
            character_uri="/".join(character_uri[:-1])
            initial_data=get_details(character_uri,graph,for_form=True)
            form = CharacterForm(initial=initial_data)
        else:
            form=CharacterForm()
        return render(request,'edit_character.html',{'form':form})
    elif request.method == "POST":
        form=CharacterForm(request.POST)

        if form.is_valid():
            if _id:
                character_uri=request.build_absolute_uri().split("/")
                character_uri="/".join(character_uri[:-1])
                update_character(form,character_uri=character_uri)
            else:
                update_character(form)
            return HttpResponse(200)
        else:
            return JsonResponse({
                'status': 'error',
                'errors': form.errors
            }, status=400)
    else:
        return HttpResponseNotAllowed(['GET','POST'])


@csrf_exempt
def delete_entity(request, uri):
    print(request)
    if request.method == "POST":
        uri = unquote(unquote(uri))  # Decode the URI
        print(f"Deleting character: {uri}")

        print("URI",uri)
        delete_query = f"""
        PREFIX sw: <http://localhost:8000/characters/>
        DELETE WHERE {{
            sw:{uri} ?p ?o .
        }}
        """


        payload_query = {"update": delete_query}
        
        try:
            response = accessor.sparql_update(body=payload_query, repo_name=repo_name)
            print("Delete response:", response)
            return JsonResponse({"success": True, "message": "Character deleted successfully."})
        except Exception as e:
            print("Error deleting character:", e)
            return JsonResponse({"success": False, "message": "Error deleting character."}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=400)



