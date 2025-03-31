import json
import logging
import re
import sys
from collections import defaultdict
from os import getenv
from urllib.parse import urlparse

from rdflib import URIRef, Literal, Namespace, RDF, RDFS, Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import networkx as nx
from pyvis.network import Network
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
from slugify import slugify

from StarwarsRDS import queries

import requests

def rdflib_graph_to_html(graph, physics_enabled=False):
    """Generates the html code for an interactible graph based on an rdflib input"""
    nx_graph = rdflib_to_networkx_graph(graph, edge_attrs=lambda s, p, o: {'label': to_human_readable(p)})

    for node in nx_graph.nodes():
        nx_graph.nodes[node]['label'] = to_human_readable(node)
        nx_graph.nodes[node]['url'] = f"/search?q={str(node)}"
        nx_graph.nodes[node]['shape'] = "box" if isinstance(node, Literal) else "circle"

    new_labels = {node: f"node_{i}" for i, node in enumerate(nx_graph.nodes(), start=1)}

    nx_graph = nx.relabel_nodes(nx_graph, new_labels, copy=False)

    net = Network(height="750px", width="100%", notebook=False, cdn_resources='remote', filter_menu=True)
    net.from_nx(nx_graph)

    net.options.physics.enabled = physics_enabled

    return net.generate_html()


def to_human_readable(node):
    """removes the uri portion of a node (or edge) and leaves only the final part (does not affect literals)"""
    if isinstance(node, URIRef):
        return re.split(r'[/#]', str(node))[-1]
    return str(node)


def is_valid_uri(
        search_string):  # apparently this divides into the components, and if it has them all, then it should be at least close enough to a valid uri to not result in an error
    parsed = urlparse(search_string)
    return all([parsed.scheme, parsed.netloc])


def get_details(uri, graph, for_form=False):
    details = defaultdict(list)

    for p, o, oName in graph.query(queries.DETAILS, initBindings={'uri': URIRef(uri)}):
        p_human = to_human_readable(p)
        if oName and not for_form:
            details[p_human].append((str(o), str(oName)))
        elif oName and for_form:
            details[p_human].append(str(oName))
        else:
            details[p_human].append(str(o))

    if for_form:
        return {key: ", ".join(lst) for key, lst in details.items()}
    else:
        return details


def get_list(type_uri, graph):
    return graph.query(queries.LIST, initBindings={"type": URIRef(type_uri)})


def update_character(form, character_uri=None):
    sw = Namespace("http://localhost:8000/characters/")
    character_ns = Namespace("http://localhost:8000/characters/")
    specie_ns = Namespace("http://localhost:8000/species/")
    planet_ns = Namespace("http://localhost:8000/planets/")

    if character_uri:
        # if already exists, remove all old triples first
        delete_query=f"""
            DELETE {{
                <{character_uri}> ?p ?o .
            }} WHERE {{
                <{character_uri}> ?p ?o .
            }}
        """
        response=requests.post(
            "http://graphdb:7200/repositories/starwars/statements",
            headers={"Content-Type": "application/sparql-update"},
            data=delete_query,
        )
        response.raise_for_status()
    else:
        character_uri = URIRef(character_ns[slugify(form.cleaned_data["label"])])

    label=form.cleaned_data["label"]
    if label:
        insert_query=f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sw: <http://localhost:8000/>
            INSERT DATA {{
                <{character_uri}> rdfs:label "{label}"
                <{character_uri}> rdf:type sw.Character
            }}
        """
        response=requests.post(
            "http://graphdb:7200/repositories/starwars/statements",
            headers={"Content-Type": "application/sparql-update"},
            data=insert_query,
        )
        response.raise_for_status()


    # add attributes
    for attribute in ["species", "gender", "species", "gender", "height", "weight", "hair_color", "eye_color",
                      "skin_color", "year_born", "year_died", "description"]:
        value = form.cleaned_data.get(attribute)
        if value:
            insert_query = f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX sw: <http://localhost:8000/>
                INSERT DATA {{
                    <{character_uri}> sw:{attribute} "{value}" .
                }}
            """
            response = requests.post(
                "http://graphdb:7200/repositories/starwars/statements",
                headers={"Content-Type": "application/sparql-update"},
                data=insert_query,
            )
            response.raise_for_status()

    # add relations
    specie = form.cleaned_data.get("species")
    if specie:
        specie_uri=URIRef(specie_ns[slugify(specie)])
        insert_query=f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX sw: <http://localhost:8000/>
            INSERT DATA {{
                <{str(character_uri)}> sw:specie <{str(specie_uri)}> .
                <{str(specie_uri)}> rdf:type <{str(sw.Specie)}> ;
                    rdfs:label "{specie}" .
            }}
        """
        response = requests.post(
            "http://graphdb:7200/repositories/starwars/statements",
            headers={"Content-Type": "application/sparql-update"},
            data=insert_query,
        )
        response.raise_for_status()

    homeworld = form.cleaned_data.get("homeworld")
    if homeworld:
        homeworld_uri = URIRef(planet_ns[slugify(homeworld)])

        insert_query = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sw: <http://localhost:8000/>
        INSERT DATA {{
                <{str(character_uri)}> sw:homeworld <{str(homeworld_uri)}> .
                <{str(homeworld_uri)}> rdf:type <{str(sw.Homeworld)}> ;
                    rdfs:label "{homeworld}" .
        }}
        """
        response = requests.post(
            "http://graphdb:7200/repositories/starwars/statements",
            headers={"Content-Type": "application/sparql-update"},
            data=insert_query,
        )
        response.raise_for_status()
