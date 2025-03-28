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

DETAILS="""
SELECT ?p ?o ?oName
WHERE{
    ?uri ?p ?o .
    OPTIONAL { ?o rdfs:label ?oName . }
}
"""

LIST="""
SELECT ?o ?oName
WHERE{
    ?o rdf:type ?type ;
       rdfs:label ?oName .
}
"""