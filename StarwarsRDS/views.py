import re

from django.http import HttpResponse
from django.shortcuts import render, redirect
from os import getenv
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from urllib.parse import unquote
from .forms import CharacterForm
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from urllib.parse import unquote


from rdflib import Graph
from rdflib.plugins.stores.sparqlstore import SPARQLStore
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable

endpoint = "http://localhost:7200/"
repo_name = "starwars"

client = ApiClient(endpoint=endpoint)

accessor = GraphDBApi(client)

#store = SPARQLStore("http://graphdb:7200/starwars", context_aware=False, returnFormat='json',
#                    method='GET') """

store = SPARQLStore("http://localhost:7200/repositories/starwars", context_aware=False, returnFormat='json',
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

# Character views

# SPARQL Query to fetch character data by URI
def get_character_data(character_uri):
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sw: <http://localhost:8000/>

    SELECT ?label ?species ?homeworld ?gender ?hair_color ?eye_color ?skin_color ?description ?height ?weight ?year_born ?year_died
    WHERE {{
      <{character_uri}> rdf:type sw:Character .
      <{character_uri}> rdfs:label ?label .
      <{character_uri}> sw:specie ?species .
      <{character_uri}> sw:homeworld ?homeworld .
      <{character_uri}> sw:gender ?gender .
      <{character_uri}> sw:hair_color ?hair_color .
      <{character_uri}> sw:eye_color ?eye_color .
      <{character_uri}> sw:skin_color ?skin_color .
      <{character_uri}> sw:description ?description .
      <{character_uri}> sw:height ?height .
      <{character_uri}> sw:weight ?weight .
      <{character_uri}> sw:year_born ?year_born .
      <{character_uri}> sw:year_died ?year_died .
    }}
    """
    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo_name)
    
    if response:
        data = json.loads(response)
        return data["results"]["bindings"]
    else:
        return []

def character_list(request):
    # Query to get all characters URIs
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX sw: <http://localhost:8000/>

    SELECT ?character
    WHERE {
      ?character rdf:type sw:Character .
    }
    """
    payload_query = {"query": query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    try:
        data = json.loads(response)  # Assuming response.text contains the JSON
        # Get a list of character URIs from the query result
        character_uris = [item["character"]["value"] for item in data["results"]["bindings"]]

        # Now fetch character data for each URI
        characters = []
        for character_uri in character_uris:
            character_data = get_character_data(character_uri)
            if character_data:
                # Extract only the first character data from the result
                character_info = {
                    'uri': character_uri,
                    'label': character_data[0].get("label", {}).get("value", "Unknown"),
                    'species': character_data[0].get("species", {}).get("value", "Unknown"),
                    'homeworld': character_data[0].get("homeworld", {}).get("value", "Unknown"),
                    'gender': character_data[0].get("gender", {}).get("value", "Unknown"),
                    'hair_color': character_data[0].get("hair_color", {}).get("value", "Unknown"),
                    'eye_color': character_data[0].get("eye_color", {}).get("value", "Unknown"),
                    'skin_color': character_data[0].get("skin_color", {}).get("value", "Unknown"),
                    'description': character_data[0].get("description", {}).get("value", "No description"),
                    'height': character_data[0].get("height", {}).get("value", "Unknown"),
                    'weight': character_data[0].get("weight", {}).get("value", "Unknown"),
                    'year_born': character_data[0].get("year_born", {}).get("value", "Unknown"),
                    'year_died': character_data[0].get("year_died", {}).get("value", "Unknown"),
                }
                characters.append(character_info)
                #print(characters)

    except Exception as e:
        print("Error while processing response:", e)
        characters = []  # Return empty list in case of an error

    # Pass the list of characters to the template
    return render(request, 'character_list.html', {'characters': characters})



# View for editing a character
def edit_character(request, character_uri):
    character_uri = unquote(unquote(character_uri))
    character_data = get_character_data(character_uri)
    print("Character Data:", character_data)
    if not character_data:
        return render(request, '404.html')  # Or any other error page
    
    character = character_data[0]  # Assuming there’s only one result
    print("hhhh")
    if request.method == 'POST':
        form = CharacterForm(request.POST)
        if form.is_valid():
            update_character(character_uri, form.cleaned_data)
            print("lololololo")
            return render('character_list') # Redirect to the character list page
    else:
        character_cleaned = {
            key: value['value'] if isinstance(value, dict) and 'value' in value else value
            for key, value in character.items()
        }
        form = CharacterForm(initial=character_cleaned)

    print("Character Data:", character)
    print("Form Data:", form)
    

    return render(request, 'edit_character_modal.html',{'form': form, 'character_uri': character_uri})

# Create your views here.

def update_character(character_uri, updated_data):
    print("ajofjjeokgmhreohkm")
    sparql_update_query = f"""
    PREFIX sw: <http://localhost:8000/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    DELETE {{
        <{character_uri}> sw:label ?label .
        <{character_uri}> sw:specie ?species .
        <{character_uri}> sw:homeworld ?homeworld .
        <{character_uri}> sw:gender ?gender .
        <{character_uri}> sw:hair_color ?hair_color .
        <{character_uri}> sw:eye_color ?eye_color .
        <{character_uri}> sw:skin_color ?skin_color .
        <{character_uri}> sw:description ?description .
        <{character_uri}> sw:height ?height .
        <{character_uri}> sw:weight ?weight .
        <{character_uri}> sw:year_born ?year_born .
        <{character_uri}> sw:year_died ?year_died .
    }} INSERT {{
        <{character_uri}> sw:label "{updated_data['label']}" .
        <{character_uri}> sw:specie "{updated_data['species']}" .
        <{character_uri}> sw:homeworld "{updated_data['homeworld']}" .
        <{character_uri}> sw:gender "{updated_data['gender']}" .
        <{character_uri}> sw:hair_color "{updated_data['hair_color']}" .
        <{character_uri}> sw:eye_color "{updated_data['eye_color']}" .
        <{character_uri}> sw:skin_color "{updated_data['skin_color']}" .
        <{character_uri}> sw:description "{updated_data['description']}" .
        <{character_uri}> sw:height "{updated_data['height']}"^^xsd:float .
        <{character_uri}> sw:weight "{updated_data['weight']}"^^xsd:float .
        <{character_uri}> sw:year_born "{updated_data['year_born']}"^^xsd:integer .
        <{character_uri}> sw:year_died "{updated_data['year_died']}"^^xsd:integer .
    }} WHERE {{
        <{character_uri}> sw:label ?label .
        <{character_uri}> sw:specie ?species .
        <{character_uri}> sw:homeworld ?homeworld .
        <{character_uri}> sw:gender ?gender .
        <{character_uri}> sw:hair_color ?hair_color .
        <{character_uri}> sw:eye_color ?eye_color .
        <{character_uri}> sw:skin_color ?skin_color .
        <{character_uri}> sw:description ?description .
        <{character_uri}> sw:height ?height .
        <{character_uri}> sw:weight ?weight .
        <{character_uri}> sw:year_born ?year_born .
        <{character_uri}> sw:year_died ?year_died .
    }}
    """

    payload_query = {"query": sparql_update_query}
    response = accessor.sparql_select(body=payload_query, repo_name=repo_name)

    print("Update response:", response)
    
    if response:
        data = json.loads(response)
        return data["results"]["bindings"]
    else:
        return []
    
    return True

def character_details(request,uri):
    print("uri",uri)
    uri = unquote(unquote(uri))
    print("ahhhhhhhhhhhhh",uri)
    character_data = get_character_data(uri)
    print("Character Data: ahhhhhhhhhhhh", character_data)  
    if not character_data:
        return render(request, '404.html')  # Or any other error page
    return render(request, 'character_details.html', {'character': character_data[0]})
