SEARCH_SUBJECT = """
        SELECT DISTINCT ?s ?p ?o ?sName
        WHERE {
            ?s ?p ?o .
            FILTER((?s = ?q && ?p = rdfs:label) || (?p = rdf:type && ?o = ?q))
            ?s rdfs:label ?sName .
        }
"""

SEARCH_OBJECT = """
            SELECT DISTINCT ?s ?sName ?p
            WHERE {
                ?s ?p ?o .
                FILTER (regex(?o,?q,"i"))
                ?s rdfs:label ?sName .
            }
        """

CONSTRUCT_LOCAL_GRAPH = """
CONSTRUCT {
        ?s rdf:type ?type ;
               ?p ?o .
    }WHERE{
        ?s rdf:type ?type ;
            ?p ?o .
    }
"""

DETAILS = """
SELECT ?p ?o ?oName
WHERE{
    ?uri ?p ?o .
    OPTIONAL { ?o rdfs:label ?oName . }
}
"""

LIST = """
SELECT ?o ?oName
WHERE{
    ?o rdf:type ?type ;
       rdfs:label ?oName .
}
"""

INSERT_CHARACTER_LABEL_AND_TYPE = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sw: <http://localhost:8000/>
    INSERT DATA {
        ?uri rdfs:label ?label ;
            rdf:type sw:Character .
    }
"""

INSERT_CHARACTER_ATTRIBUTES="""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sw: <http://localhost:8000/>
    INSERT DATA {
        ?uri ?attribute ?value .
    }
"""

INSERT_CHARACTER_SPECIE="""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sw: <http://localhost:8000/>
    INSERT DATA {
        ?character_uri sw:specie ?specie_uri .
        ?specie_uri rdf:type sw:Specie ;
            rdfs:label ?specie .
    }
"""

INSERT_CHARACTER_HOMEWORLD="""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX sw: <http://localhost:8000/>
    INSERT DATA {
        ?character_uri sw:homeworld ?homeworld_uri .
        ?homeworld_uri rdf:type sw:Planet ;
        rdfs:label ?homeworld .
    }
"""

IS_URI_REFERENCED = """
    ASK { ?s ?p ?uri . }
"""

DELETE_ALL_DATA = """
DELETE {
    ?uri ?p ?o .
} WHERE {
    ?uri ?p ?o .
}
"""

# in order to avoid 404s, we have decided that all referenced URIs (as in, all URIs that appear as objects) must have at least their label and type specified
DELETE_DATA_REFERENCE_SAFE = """
    DELETE WHERE {
        ?uri ?p ?o .
        FILTER(?p != rdf:type && ?p != rdfs:label)
    }
"""
