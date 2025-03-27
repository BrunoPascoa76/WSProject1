import json
import re
from urllib.parse import urlparse


from rdflib import URIRef, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import networkx as nx
from pyvis.network import Network

def rdflib_graph_to_html(graph,physics_enabled=False):
    """Generates the html code for an interactible graph based on an rdflib input"""
    nx_graph=rdflib_to_networkx_graph(graph,edge_attrs=lambda s,p,o: {'label': to_human_readable(p)})

    for node in nx_graph.nodes():
        nx_graph.nodes[node]['label'] = to_human_readable(node)
        nx_graph.nodes[node]['url']=f"/search?q={str(node)}"
        nx_graph.nodes[node]['shape']="box" if isinstance(node,Literal) else "circle"

    new_labels = {node: f"node_{i}" for i, node in enumerate(nx_graph.nodes(), start=1)}

    nx_graph=nx.relabel_nodes(nx_graph,new_labels,copy=False)


    net=Network(height="750px",width="100%",notebook=False,cdn_resources='remote',filter_menu=True)
    net.from_nx(nx_graph)

    net.options.physics.enabled = physics_enabled

    return net.generate_html()

def to_human_readable(node):
    """removes the uri portion of a node (or edge) and leaves only the final part (does not affect literals)"""
    if isinstance(node, URIRef):
        return re.split(r'[/#]',str(node))[-1]
    return str(node)

def is_valid_uri(search_string): #apparently this divides into the components, and if it has them all, then it should be at least close enough to a valid uri to not result in an error
    parsed=urlparse(search_string)
    return all([parsed.scheme,parsed.netloc])
