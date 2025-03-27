import re
from collections import defaultdict
from unittest import case
from os import getenv

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from os import getenv
from rdflib.plugins.sparql import prepareQuery, prepareUpdate
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote
from .forms import CharacterAttributesForm, CharacterRelationsForm
import json
from s4api.graphdb_api import GraphDBApi
from s4api.swagger import ApiClient
from urllib.parse import unquote

from rdflib import Graph, URIRef, Literal, RDFS, RDF
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from .utils import rdflib_graph_to_html, is_valid_uri, to_human_readable

endpoint = "http://localhost:7200/"
repo_name = "starwars"

client = ApiClient(endpoint=endpoint)

accessor = GraphDBApi(client)

store = SPARQLUpdateStore("http://localhost:7200/repositories/starwars", context_aware=False, returnFormat='json')
graph = Graph(store)

# Uncomment the following lines if you want to use the GraphDB SPARQLStore in docker
""" store = SPARQLUpdateStore(getenv("GRAPHDB_URL"), getenv("GRAPHDB_UPDATE_URL"), context_aware=False)
graph = Graph(store) """


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

def description(request, _type, _name):
    match request.method:
        case 'GET':
            return 0
            #return get_description(request)
        case 'POST':
            #return add_description(request)
            return 0
        case 'PUT':
            #return update_description(request)
            return 0
        case 'DELETE':
            #return delete_description(request)
            return 0


#def get_description(request):
#    uri = request.build_absolute_uri()
#    attributes = defaultdict(list)
#    relations = defaultdict(list)

    # will need to divide between triples where the object is a literal ("attributes") and ones where the objects is a URI ("relations") for later (because on update, I need to know whether  I need to add the type for consistency's sake
#    attributes_query = """
#        SELECT ?p ?o
#        WHERE {
#            ?uri ?p ?o .
#        }
#    """
#    uri=request.build_absolute_uri()[:-1] #to remove the last "/"
#    local_graph=graph.query(query,initBindings={'type':URIRef(uri)}).graph    
#    print("Attributes:", attributes)
#    print("Relations:", relations)

#    return render(request, 'home.html', {'graph_html': rdflib_graph_to_html(local_graph)})# Character views

def get_character_data(character_uri):
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sw: <http://localhost:8000/>

    SELECT ?label ?species ?homeworld ?gender ?hair_color ?eye_color ?skin_color ?description ?height ?weight ?year_born ?year_died ?homeworld_label ?species_label
    WHERE {{
      <{character_uri}> rdf:type sw:Character .
      <{character_uri}> rdfs:label ?label .
      <{character_uri}> sw:specie ?species .
      ?species rdfs:label ?species_label .
      <{character_uri}> sw:homeworld ?homeworld .
      ?homeworld rdfs:label ?homeworld_label .
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
                    'homeworld_label': character_data[0].get("homeworld_label", {}).get("value", "Unknown"),
                    'species_label': character_data[0].get("species_label", {}).get("value", "Unknown")
                }
                characters.append(character_info)
                print(characters)

    except Exception as e:
        print("Error while processing response:", e)
        characters = []  # Return empty list in case of an error

    # Pass the list of characters to the template
    return render(request, 'character_list.html', {'characters': characters})


def character_details(request,uri):
    uri = unquote(unquote(uri))
    character_data = get_character_data(uri)
    character_data[0]['uri'] = uri
    print("Character Data: ahhhhhhhhhhhh", character_data)  
    if not character_data:
        return render(request, '404.html')  # Or any other error page
    return render(request, 'character_details.html', {'character': character_data[0]})


@csrf_exempt
def delete_character(request, uri):
    if request.method == "POST":
        uri = unquote(unquote(uri))  # Decode the URI
        print(f"Deleting character: {uri}")

        delete_query = f"""
        PREFIX sw: <http://localhost:8000/>
        DELETE WHERE {{
            <{uri}> ?p ?o .
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

def edit_character_attributes(request, uri):
    # Fetch character data using the custom query function
    character_data = get_character_data(uri)
    print("character_data",character_data)

    if not character_data:
        return JsonResponse({'error': 'Character not found'}, status=404)

    initial_data = {
        'label': character_data[0].get("label", {}).get("value", ""),
        'gender': character_data[0].get('gender', {}).get('value', ''),
        'hair_color': character_data[0].get('hair_color', {}).get('value', ''),
        'eye_color': character_data[0].get('eye_color', {}).get('value', ''),
        'skin_color': character_data[0].get('skin_color', {}).get('value', ''),
        'description': character_data[0].get('description', {}).get('value', ''),
        'height': character_data[0].get('height', {}).get('value', ''),
        'weight': character_data[0].get('weight', {}).get('value', ''),
        'year_born': character_data[0].get('year_born', {}).get('value', ''),
        'year_died': character_data[0].get('year_died', {}).get('value', ''),
    }

    print(initial_data)

    if request.method == "POST":
        form = CharacterAttributesForm(request.POST)
        if form.is_valid():
            # Update character attributes based on the form
            updated_character = {
                'label': form.cleaned_data['label'],
                'gender': form.cleaned_data['gender'],
                'hair_color': form.cleaned_data['hair_color'],
                'eye_color': form.cleaned_data['eye_color'],
                'skin_color': form.cleaned_data['skin_color'],
                'description': form.cleaned_data['description'],
                'height': form.cleaned_data['height'],
                'weight': form.cleaned_data['weight'],
                'year_born': form.cleaned_data['year_born'],
                'year_died': form.cleaned_data['year_died'],
            }

            # Save the updated character attributes
            # You may need to update your SPARQL endpoint here to update the data accordingly
            # For now, we simulate saving
            # character.save(updated_character)

            return JsonResponse({'message': 'Character attributes updated successfully!'})
    else:
        form = CharacterAttributesForm(initial=initial_data)

    return render(request, "edit_character_attributes.html", {"form": form})


def edit_character_relations(request, uri):
    # Fetch character data using the custom query function
    print("uri", uri)
    character_data = get_character_data(uri)

    if not character_data:
        return JsonResponse({'error': 'Character not found'}, status=404)

    # Extract relations (species and homeworld)
    character_relations = {
        'species': character_data[0]['species']['value'],
        'homeworld': character_data[0]['homeworld']['value'],
    }

    # Query for species data
    query = """
    SELECT ?species ?label
    WHERE {
        ?species rdf:type <http://localhost:8000/Specie> .
        OPTIONAL { ?species <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
    }
    """

    # Execute the query
    results = graph.query(query)

    species = {
        str(result[0]): {'name': str(result[1]) if result[1] else "Unknown"}
        for result in results
    }

    # Query for planets data (homeworlds)
    query = """
    SELECT ?planet ?label
    WHERE {
        ?planet rdf:type <http://localhost:8000/Planet> .
        ?planet <http://www.w3.org/2000/01/rdf-schema#label> ?label . 
    }
    """

    # Execute the query
    results = graph.query(query)

    planets = {}

    for result in results:
        planet_url = str(result[0])
        planet_name = str(result[1]) if result[1] else "Unknown"

        planets[planet_url] = {'name': planet_name}

    print(planets)

    initial_data = {
        'species': character_relations.get('species', ''),
        'homeworld': character_relations.get('homeworld', ''),
    }

    if request.method == "POST":
        form = CharacterRelationsForm(request.POST, available_species=species, available_homeworlds=planets)
        if form.is_valid():
            # Update character relations based on the form
            updated_relations = {
                'species': form.cleaned_data['species'],
                'homeworld': form.cleaned_data['homeworld'],
            }

            # Save the updated relations (you may need to update your SPARQL endpoint here)
            return JsonResponse({'message': 'Character relations updated successfully!'})
    else:
        form = CharacterRelationsForm(initial=initial_data, available_species=species, available_homeworlds=planets)

    return render(request, "edit_character_relations.html", {
        'form': form,
        'available_species': species,
        'available_homeworlds': planets,
    })


#Films Views

def getAllFilms(request):
    query = """
    SELECT ?film ?label ?release_date
    WHERE {
        ?film rdf:type <http://localhost:8000/Film> .
        OPTIONAL { ?film <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
        OPTIONAL { ?film <http://localhost:8000/release_date> ?release_date . }
    }
    """

    results = graph.query(query)

    films = {}

    for result in results:
        film_url = str(result[0])  
        film_name = str(result[1]) if result[1] else "Unknown"
        release_date = str(result[2]) if result[2] else "Unknown"

        films[film_url] = {
            'name': film_name,
            'release_date': release_date
        }

    print(films)

    return render(request, 'films.html', {'films': films})

def film_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'film_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })


##Droids Views

def getAllDroids(request):
    query = """
    SELECT ?droid ?label
    WHERE {
        ?droid rdf:type <http://localhost:8000/Droid> .
        OPTIONAL { ?droid <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
    }
    """

    results = graph.query(query)

    droids = {}

    for result in results:
        droid_url = str(result[0])  
        droid_name = str(result[1]) if result[1] else "Unknown"

        droids[droid_url] = {'name': droid_name}

    print(droids)

    return render(request, 'droids.html', {'droids': droids})

def droid_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'droid_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })



#Cities Views

def getAllCities(request):
    query = """
    SELECT ?city ?cityLabel ?planet ?planetLabel
    WHERE {
        ?city rdf:type <http://localhost:8000/City> .
        OPTIONAL { ?city <http://www.w3.org/2000/01/rdf-schema#label> ?cityLabel . }
        OPTIONAL { 
            ?city <http://localhost:8000/planet> ?planet .
            OPTIONAL { ?planet <http://www.w3.org/2000/01/rdf-schema#label> ?planetLabel . }
        }
    }
    """

    results = graph.query(query)

    cities = {}

    for result in results:
        city_url = str(result[0])
        city_name = str(result[1]) if result[1] else "Unknown"
        planet_url = str(result[2]) if result[2] else None
        planet_name = str(result[3]) if result[3] else "Unknown"

        if city_url not in cities:
            cities[city_url] = {'name': city_name, 'planets': {}}

        if planet_url:
            cities[city_url]['planets'][planet_url] = {'name': planet_name}

    print(cities)

    return render(request, 'cities.html', {'cities': cities})

def city_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = {}
    relations = {}

    # Query to get all attributes of the city
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable] = value

    # Query to get all relations of the city
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable] = value

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'city_details.html', {
        'label': attributes.get("label", "Unknown"),
        'attributes': attributes,
        'relations': relations
    })


#Music Views

def getAllMusic(request):
    query = """
    SELECT ?music ?musicLabel ?movie ?movieLabel
    WHERE {
        ?music rdf:type <http://localhost:8000/Music> .
        OPTIONAL { ?music <http://www.w3.org/2000/01/rdf-schema#label> ?musicLabel . }
        OPTIONAL { 
            ?music <http://localhost:8000/associated_with> ?movie .
            OPTIONAL { ?movie <http://www.w3.org/2000/01/rdf-schema#label> ?movieLabel . }
        }
    }
    """
    
    # Execute the optimized query
    results = graph.query(query)

    music_data = {}

    for result in results:
        music_url = str(result[0])
        music_label = str(result[1]) if result[1] else "Unknown"
        movie_url = str(result[2]) if result[2] else None
        movie_label = str(result[3]) if result[3] else "Unknown"

        # Ensure the music entry exists in the dictionary
        if music_url not in music_data:
            music_data[music_url] = {
                'music_label': music_label,
                'movies': {}  # Store associated movies here
            }

        # Add movie details if available
        if movie_url:
            music_data[music_url]['movies'][movie_url] = {'movie_label': movie_label}

    print(music_data)

    return render(request, 'music.html', {'music_data': music_data})

def music_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = {}
    relations = {}

    # Query to get all attributes of the city
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable] = value

    # Query to get all relations of the city
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable] = value

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'music_details.html', {
        'label': attributes.get("label", "Unknown"),
        'attributes': attributes,
        'relations': relations
    })




#Organizations Views

def getAllOrganizations(request):
    query = """
    SELECT ?organization ?label
    WHERE {
        ?organization rdf:type <http://localhost:8000/Organization> .
        ?organization <http://www.w3.org/2000/01/rdf-schema#label> ?label . 
    }
    """
    
    # Execute the query
    results = graph.query(query)

    organizations = {}

    for result in results:
        organization_url = str(result[0])
        organization_name = str(result[1]) if result[1] else "Unknown"

        organizations[organization_url] = {'name': organization_name}

    print(organizations)

    return render(request, 'organizations.html', {'organizations': organizations})

def organization_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'organization_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })



#Planets Views
def getAllPlanets(request):
    query = """
    SELECT ?planet ?label
    WHERE {
        ?planet rdf:type <http://localhost:8000/Planet> .
        ?planet <http://www.w3.org/2000/01/rdf-schema#label> ?label . 
    }
    """

    # Execute the query
    results = graph.query(query)

    planets = {}

    for result in results:
        planet_url = str(result[0])
        planet_name = str(result[1]) if result[1] else "Unknown"

        planets[planet_url] = {'name': planet_name}

    print(planets)

    return render(request, 'planets.html', {'planets': planets})

def planet_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'planet_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })

#Quotes Views

def getAllQuotes(request):
    query = """
    SELECT ?quote ?quoteLabel ?character ?characterLabel ?movie ?movieLabel
    WHERE {
        ?quote rdf:type <http://localhost:8000/Quote> .
        OPTIONAL { ?quote <http://www.w3.org/2000/01/rdf-schema#label> ?quoteLabel . }
        OPTIONAL { ?quote <http://localhost:8000/said_by> ?character . }
        OPTIONAL { ?character <http://www.w3.org/2000/01/rdf-schema#label> ?characterLabel . }
        OPTIONAL { ?quote <http://localhost:8000/appears_in> ?movie . }
        OPTIONAL { ?movie <http://www.w3.org/2000/01/rdf-schema#label> ?movieLabel . }
    }
    """

    # Execute the query
    results = graph.query(query)

    quotes = {}

    for result in results:
        quote_url = str(result["quote"]) if result["quote"] else "Unknown"
        quote_text = str(result["quoteLabel"]) if result["quoteLabel"] else "Unknown"
        character_url = str(result["character"]) if result["character"] else None
        character_name = str(result["characterLabel"]) if result["characterLabel"] else "Unknown"
        movie_url = str(result["movie"]) if result["movie"] else None
        movie_name = str(result["movieLabel"]) if result["movieLabel"] else "Unknown"

        quotes[quote_url] = {
            "character_url": character_url,
            "character_name": character_name,
            "film_url": movie_url,
            "film_name": movie_name,
            "label": quote_text
        }

    print(quotes)

    return render(request, "quotes.html", {"quotes": quotes})

def quote_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'quote_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })


#Species Views

def getAllSpecies(request):
    query = """
    SELECT ?species ?label
    WHERE {
        ?species rdf:type <http://localhost:8000/Specie> .
        OPTIONAL { ?species <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
    }
    """

    # Execute the query
    results = graph.query(query)

    species = {
        str(result[0]): {'name': str(result[1]) if result[1] else "Unknown"}
        for result in results
    }

    return render(request, 'species.html', {'species': species})

def specie_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'species_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })



#Starships Views

def getAllStarships(request):
    query = """
    SELECT ?starship ?label ?class
    WHERE {
        ?starship rdf:type <http://localhost:8000/Starship> .
        OPTIONAL { ?starship <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
        OPTIONAL { ?starship <http://localhost:8000/starship_class> ?class . }
    }
    """

    # Execute the query
    results = graph.query(query)

    starships = {
        str(result[0]): {
            'name': str(result[1]) if result[1] else "Unknown",
            'class': str(result[2]) if result[2] else "Unknown"
        }
        for result in results
    }

    return render(request, 'starships.html', {'starships': starships})

def starship_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'starship_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })


    
# Vehicles Views

def getAllVehicles(request):
    query = """
    SELECT ?vehicle ?label ?class
    WHERE {
        ?vehicle rdf:type <http://localhost:8000/Vehicle> .
        OPTIONAL { ?vehicle <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
        OPTIONAL { ?vehicle <http://localhost:8000/vehicle_class> ?class . }
    }
    """

    # Execute the query
    results = graph.query(query)

    vehicles = {
        str(result[0]): {
            'name': str(result[1]) if result[1] else "Unknown",
            'class': str(result[2]) if result[2] else "Unknown"
        }
        for result in results
    }

    return render(request, 'vehicles.html', {'vehicles': vehicles})

def vehicle_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'vehicle_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })



# Weapons Views

def getAllWeapons(request):
    query = """
    SELECT ?weapon ?label ?model ?type
    WHERE {
        ?weapon rdf:type <http://localhost:8000/Weapon> .
        OPTIONAL { ?weapon <http://www.w3.org/2000/01/rdf-schema#label> ?label . }
        OPTIONAL { ?weapon <http://localhost:8000/model> ?model . }
        OPTIONAL { ?weapon <http://localhost:8000/type> ?type . }
    }
    """

    # Execute the query
    results = graph.query(query)

    weapons = {
        str(result[0]): {
            'name': str(result[1]) if result[1] else "Unknown",
            'model': str(result[2]) if result[2] else "Unknown",
            'type': str(result[3]) if result[3] else "Unknown"
        }
        for result in results
    }

    return render(request, 'weapons.html', {'weapons': weapons})

def weapon_details(request, uri):
    print("uri", uri)
    uri = unquote(unquote(uri))
    print("Decoded URI:", uri)

    attributes = defaultdict(list)  # Use a defaultdict to store lists
    relations = defaultdict(list)  # Use a defaultdict to store lists

    # Query to get all attributes of the droid
    attributes_query = """
        SELECT ?p ?o
        WHERE {
            ?uri ?p ?o .
        }
    """

    for p, o in graph.query(attributes_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = o.toPython() if isinstance(o, Literal) else str(o)  # Convert to a readable format
        attributes[p_human_readable].append(value)  # Append to the list if multiple values exist

    # Query to get all relations of the droid
    relations_query = """
        SELECT DISTINCT ?p ?o ?oLabel
        WHERE {
            ?uri ?p ?o .
            OPTIONAL { ?o rdfs:label ?oLabel . }
        }
    """

    for p, o, oLabel in graph.query(relations_query, initBindings={"uri": URIRef(uri)}):
        p_human_readable = to_human_readable(p)
        value = oLabel.toPython() if isinstance(oLabel, Literal) else str(o)  # Prefer human-readable label
        relations[p_human_readable].append(value)  # Append to the list if multiple relations exist

    print("Formatted Attributes:", attributes)
    print("Formatted Relations:", relations)

    if not attributes:
        return render(request, '404.html')  # Return an error page if no data is found

    return render(request, 'weapon_details.html', {
        'label': attributes.get("label", ["Unknown"])[0],  # Get first value if available
        'attributes': attributes,
        'relations': relations
    })

