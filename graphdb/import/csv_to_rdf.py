import csv
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD
from slugify import slugify

SERVER_PREFIX="http://localhost:8000"

sw=Namespace(f"{SERVER_PREFIX}/")
character_ns=Namespace(f"{SERVER_PREFIX}/characters/")
city_ns=Namespace(f"{SERVER_PREFIX}/cities/")
droid_ns=Namespace(f"{SERVER_PREFIX}/droids/")
film_ns=Namespace(f"{SERVER_PREFIX}/films/")
music_ns=Namespace(f"{SERVER_PREFIX}/music/")
organisation_ns=Namespace(f"{SERVER_PREFIX}/organisations/")
planet_ns=Namespace(f"{SERVER_PREFIX}/planets/")
quote_ns=Namespace(f"{SERVER_PREFIX}/quotes/")
specie_ns=Namespace(f"{SERVER_PREFIX}/species/")
starship_ns=Namespace(f"{SERVER_PREFIX}/starships/")
vehicle_ns=Namespace(f"{SERVER_PREFIX}/vehicles/")
weapon_ns=Namespace(f"{SERVER_PREFIX}/weapons/")

g=Graph()
g.bind("sw",sw)
g.bind("character",character_ns)
g.bind("city",city_ns)
g.bind("droid",droid_ns)
g.bind("film",film_ns)
g.bind("music",music_ns)
g.bind("organization",organisation_ns)
g.bind("planet",planet_ns)
g.bind("quote",quote_ns)
g.bind("specie",specie_ns)
g.bind("starship",starship_ns)
g.bind("vehicle",vehicle_ns)
g.bind("weapon",weapon_ns)

with open("characters.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        character_uri = URIRef(character_ns[slugify(row["name"])])
        g.add((character_uri,RDF.type,sw.Character))
        g.add((character_uri,RDFS.label,Literal(row["name"])))

        #species relation
        specie_uri=URIRef(specie_ns[slugify(row["specie"])])
        g.add((character_uri,sw.specie,specie_uri))

        #homeworld relation
        homeworld_uri=URIRef(planet_ns[slugify(row["homeworld"])])
        g.add((character_uri,sw.homeworld,homeworld_uri))

        #attributes
        for string_attribute in ["gender","hair_color","eye_color","skin_color","description"]:
            if row[string_attribute]:
                g.add((character_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["height","weight"]:
            if row[float_attribute]:
                g.add((character_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for integer_attribute in ["year_born","year_died"]:
            if row[integer_attribute]:
                g.add((character_uri,sw[integer_attribute],Literal(row[integer_attribute],datatype=XSD.integer)))



with open("cities.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        city_uri=URIRef(city_ns[slugify(row["name"])])
        g.add((city_uri,RDF.type,sw.City))
        g.add((city_uri,RDFS.label,Literal(row["name"])))

        #planet relation
        planet_uri=URIRef(planet_ns[slugify(row["planet"])])
        g.add((city_uri,sw.planet,planet_uri))

        #attributes
        g.add((city_uri,sw.population,Literal(row["population"],datatype=XSD.integer)))
        g.add((city_uri,sw.description,row["description"]))



with open("droids.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        droid_uri=URIRef(droid_ns[slugify(row["name"])])
        g.add((droid_uri,RDF.type,sw.Droid))
        g.add((droid_uri,RDFS.label,Literal(row["name"])))

        #films relation
        for film in row["films"].split(', '):
            film_uri=URIRef(film_ns[slugify(film)])
            g.add((droid_uri,sw.appears_in,film_uri))

        #attributes
        for string_attribute in ["model","manufacturer","sensor_color","primary_function"]:
            if row[string_attribute]:
                g.add((droid_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["height","mass"]:
            if row[float_attribute]:
                g.add((droid_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for plating_color in row["plating_colors"].split('/'): #splitting just in case we need it for search
            g.add((droid_uri,sw.plating_color,plating_color))



with open("films.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        film_uri=URIRef(film_ns[slugify(row["title"])])
        g.add((film_uri,RDF.type,sw.Film))
        g.add((film_uri,RDFS.label,Literal(row["title"])))
        g.add((film_uri,sw.release_date,Literal(row["release_date"],datatype=XSD.date)))
        g.add((film_uri,sw.director,Literal(row["director"])))
        g.add((film_uri,sw.opening_crawl,Literal(row["opening_crawl"])))

        for producer in row["producers"].split(','):
            producer=producer.strip().replace('"','')
            g.add((film_uri, sw.producer, Literal(producer)))



with open("music.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        music_uri=URIRef(music_ns[slugify(row["title"])])
        g.add((music_uri,RDF.type,sw.Music))
        g.add((music_uri,RDFS.label,Literal(row["title"])))
        g.add((music_uri,sw.composer,Literal(row["composer"])))
        g.add((music_uri,sw.type,Literal(row["type"])))

        film_uri=URIRef(film_ns[slugify(row["associated_with"])])
        g.add((music_uri,sw.associated_with,film_uri))



with open("organizations.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        organization_uri=URIRef(organisation_ns[slugify(row["name"])])
        g.add((organization_uri,RDF.type,sw.Organization))
        g.add((organization_uri,RDFS.label,Literal(row["name"])))
        g.add((organization_uri,sw.founded,Literal(row["founded"],datatype=XSD.integer)))
        g.add((organization_uri,sw.dissolved,Literal(row["dissolved"],datatype=XSD.integer)))
        g.add((organization_uri,sw.description,Literal(row["description"])))

        for leader in row["leader"].split(", "):
            leader=leader.strip().replace('"','')
            leader_uri=URIRef(character_ns[slugify(leader)])

            g.add((organization_uri, sw.leader,leader_uri))

        for member in row["members"].split(", "):
            member=member.strip().replace('"','')
            member_uri=URIRef(character_ns[slugify(member)])
            g.add((organization_uri, sw.member,member_uri))

        if row["affiliation"] is not None and row["affiliation"]!="None":
            g.add((organization_uri,sw.affiliation,row["affiliation"]))


        for film in row["films"].split(", "):
            film=film.strip().replace('"','')
            film_uri=URIRef(film_ns[slugify(film)])
            g.add((film_uri,sw.appears_in,film_uri))

        if row["affiliation"] is not None:
            g.add((organization_uri, sw.affiliation, Literal(row["affiliation"])))

rdf_xml=g.serialize(format="xml")

with open("characters.xml","w") as f:
    f.write(rdf_xml)



