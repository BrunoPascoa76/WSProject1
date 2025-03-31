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

def remove_entity(graph,uri):
    is_uri_mentioned=graph.query(queries.IS_URI_REFERENCED,initBindings={'uri': URIRef(uri)})

    if bool(is_uri_mentioned):
        delete_query=queries.DELETE_DATA_REFERENCE_SAFE.replace("?uri",f"<{uri}>")
    else:
        delete_query=queries.DELETE_ALL_DATA.replace("?uri",f"<{uri}>")

    response = requests.post(
        "http://graphdb:7200/repositories/starwars/statements",
        headers={"Content-Type": "application/sparql-update"},
        data=delete_query,
    )

    response.raise_for_status()


def update_character(form, character_uri=None):
    sw = Namespace("http://localhost:8000/characters/")
    character_ns = Namespace("http://localhost:8000/characters/")
    specie_ns = Namespace("http://localhost:8000/species/")
    planet_ns = Namespace("http://localhost:8000/planets/")

    if character_uri:
        # if already exists, remove all old triples first
        delete_query=queries.DELETE_ALL_DATA.replace("?uri",f"<{character_uri}>")
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
        insert_query=queries.INSERT_CHARACTER_LABEL_AND_TYPE.replace("?uri",f"<{character_uri}>").replace("?label",f'"{label}"')
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
            insert_query = queries.INSERT_CHARACTER_ATTRIBUTES.replace("?uri",f"<{character_uri}>").replace("?attribute",f"sw:{attribute}").replace("?value",f'"{value}"')
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
        insert_query=queries.INSERT_CHARACTER_SPECIE.replace("?character_uri",f"<{character_uri}>").replace("?specie_uri",f"<{specie_uri}>").replace("?specie",f'"{specie}"')
        response = requests.post(
            "http://graphdb:7200/repositories/starwars/statements",
            headers={"Content-Type": "application/sparql-update"},
            data=insert_query,
        )
        response.raise_for_status()

    homeworld = form.cleaned_data.get("homeworld")
    if homeworld:
        homeworld_uri = URIRef(planet_ns[slugify(homeworld)])

        insert_query = queries.INSERT_CHARACTER_HOMEWORLD.replace("?character_uri",f"<{character_uri}>").replace("?homeworld_uri",f"<{homeworld_uri}>").replace("?homeworld",f'"{homeworld}"')
        response = requests.post(
            "http://graphdb:7200/repositories/starwars/statements",
            headers={"Content-Type": "application/sparql-update"},
            data=insert_query,
        )
        response.raise_for_status()
