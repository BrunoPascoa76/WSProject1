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

#Note: Since the author uses names/titles as "private keys", I will be using them for the URIs (except for quotes, since it only has ids).
#It should also be noted that some files are missing (events, battles and timeline) because they were either incomplete or had type ambiguity (for example, the victors of battles could be either organizations or a planet('s inhabitants))

with open("characters.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        character_uri = URIRef(character_ns[slugify(row["name"])])
        g.add((character_uri,RDF.type,sw.Character))
        g.add((character_uri,RDFS.label,Literal(row["name"])))

        #species relation
        specie_uri=URIRef(specie_ns[slugify(row["species"])])
        g.add((character_uri,sw.specie,specie_uri))
        g.add((specie_uri,RDF.type,sw.Specie))
        g.add((specie_uri,RDFS.label,Literal(row["species"])))

        #homeworld relation
        if row["homeworld"]!="Unknown":
            homeworld_uri=URIRef(planet_ns[slugify(row["homeworld"])])
            g.add((character_uri,sw.homeworld,homeworld_uri))
            #I added both of these in case they were missing from planets.csv (much like with a set, a rdf graph only adds each triple once, so we can do this without worrying)
            g.add((homeworld_uri,RDF.type,sw.Planet))
            g.add((homeworld_uri, RDFS.label, Literal(row["homeworld"])))

        #attributes
        for string_attribute in ["gender","hair_color","eye_color","skin_color","description"]:
            if row[string_attribute] and row[string_attribute]!="None" and row[string_attribute]!="Unknown":
                g.add((character_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["height","weight"]:
            if row[float_attribute] and row[float_attribute]!="None" and row[float_attribute]!="Unknown":
                g.add((character_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for integer_attribute in ["year_born","year_died"]:
            if row[integer_attribute] and row[integer_attribute]!="None" and row[integer_attribute]!="Unknown":
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
        g.add((planet_uri,RDF.type,sw.Planet))
        g.add((planet_uri,RDFS.label,Literal(row["planet"])))

        #attributes
        g.add((city_uri,sw.population,Literal(row["population"],datatype=XSD.integer)))
        g.add((city_uri,sw.description,Literal(row["description"])))



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
            g.add((film_uri,RDF.type,sw.Film))
            g.add((film_uri,RDFS.label,Literal(film)))

        #attributes
        for string_attribute in ["model","manufacturer","sensor_color","primary_function"]:
            if row[string_attribute]:
                g.add((droid_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["height","mass"]:
            if row[float_attribute]:
                g.add((droid_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for plating_color in row["plating_color"].split('/'): #splitting incase we want to search for individual plating colors
            g.add((droid_uri,sw.plating_color,Literal(plating_color)))



with open("films.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        film_uri=URIRef(film_ns[slugify(row["title"])])
        g.add((film_uri,RDF.type,sw.Film))
        g.add((film_uri,RDFS.label,Literal(row["title"])))
        g.add((film_uri,sw.release_date,Literal(row["release_date"],datatype=XSD.date)))
        g.add((film_uri,sw.director,Literal(row["director"])))
        g.add((film_uri,sw.opening_crawl,Literal(row["opening_crawl"])))

        for producer in row["producer"].split(','):
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
        g.add((film_uri,RDF.type,sw.Film))
        g.add((film_uri,RDFS.label,Literal(row["associated_with"])))



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
            leader_uri=URIRef(character_ns[slugify(leader)])
            g.add((organization_uri, sw.leader,leader_uri))
            g.add((leader_uri,RDF.type,sw.Character))
            g.add((leader_uri, RDFS.label,Literal(leader)))

        for member in row["members"].split(", "):
            member_uri=URIRef(character_ns[slugify(member)])
            g.add((organization_uri, sw.member,member_uri))
            g.add((member_uri,RDF.type,sw.Character))
            g.add((member_uri, RDFS.label,Literal(member)))

        if row["affiliation"] is not None and row["affiliation"]!="None":
            g.add((organization_uri,sw.affiliation,Literal(row["affiliation"])))


        for film in row["films"].split(", "):
            film_uri=URIRef(film_ns[slugify(film)])
            g.add((organization_uri,sw.appears_in,film_uri))
            g.add((film_uri,RDF.type,sw.Film))
            g.add((film_uri,RDFS.label,Literal(film)))


with open("planets.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        planet_uri=URIRef(planet_ns[slugify(row["name"])])
        g.add((planet_uri,RDF.type,sw.Planet))
        g.add((planet_uri,RDFS.label,Literal(row["name"])))
        g.add((planet_uri,sw.gravity,Literal(row["gravity"])))
        g.add((planet_uri,sw.climate,Literal(row["climate"])))

        if row["population"] is not None:
            g.add((planet_uri,sw.population,Literal(row["population"])))

        for float_attribute in ['diameter','rotation_period','orbital_period','surface_water']:
            if row[float_attribute]:
                g.add((planet_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for terrain in row["terrain"].split(", "):
            g.add((planet_uri,sw.terrain,Literal(terrain)))

        for resident in row["residents"].split(", "):
            character_uri=URIRef(character_ns[slugify(resident)])
            g.add((planet_uri,sw.resident,character_uri))
            g.add((character_uri,RDF.type,sw.Character))
            g.add((character_uri,RDFS.label,Literal(resident)))

        if row["films"]:
            for film in row["films"].split(", "):
                film_uri=URIRef(film_ns[slugify(film)])
                g.add((planet_uri,sw.appears_in,film_uri))
                g.add((film_uri,RDF.type,sw.Film))
                g.add((film_uri,RDFS.label,Literal(film)))



with open("quotes.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        quote_uri = URIRef(quote_ns[slugify(row["id"])])
        g.add((quote_uri, RDF.type, sw.Quote))

        # Add the quote text
        g.add((quote_uri, RDFS.label, Literal(row["quote"])))

        character_uri = URIRef(character_ns[slugify(row["character_name"])])
        g.add((quote_uri, sw.said_by, character_uri))
        g.add((character_uri, RDF.type, sw.Character))
        g.add((character_uri, RDFS.label, Literal(row["character_name"])))

        source_uri = URIRef(film_ns[slugify(row["source"])])
        g.add((quote_uri, sw.appears_in, source_uri))
        g.add((source_uri, RDF.type, sw.Film))
        g.add((source_uri, RDFS.label, Literal(row["source"])))



with open("species.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        specie_uri=URIRef(specie_ns[slugify(row["name"])])
        g.add((specie_uri,RDF.type,sw.Specie))
        g.add((specie_uri,RDFS.label,Literal(row["name"])))

        for string_attribute in ["classification","designation","hair_colors","eye_colors","language"]:
            if row[string_attribute] and row[string_attribute]!="None" and row[string_attribute]!="Unknown":
                g.add((specie_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["average_height","average_lifespan"]:
            if row[float_attribute]:
                g.add((specie_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        if row["skin_colors"]!="Unknown":
            for skin_color in row["skin_colors"].split(", "):
                g.add((specie_uri,sw.skin_color,Literal(skin_color)))

        if row["homeworld"]!="None" and row["homeworld"]!="Unknown":
            homeworld_uri=URIRef(planet_ns[slugify(row["homeworld"])])
            g.add((specie_uri,sw.homeworld,homeworld_uri))
            g.add((homeworld_uri,RDF.type,sw.Planet))
            g.add((homeworld_uri,RDFS.label,Literal(row["homeworld"])))



with open("starships.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        starship_uri=URIRef(starship_ns[slugify(row["name"])])
        g.add((starship_uri,RDF.type,sw.Starship))
        g.add((starship_uri,RDFS.label,Literal(row["name"])))

        for float_attribute in ["cost_in_credits","length","max_atmosphering_speed","cargo_capacity","hyperdrive_rating"]:
            if row[float_attribute]:
                g.add((starship_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for integer_attribute in ["crew","passengers","MGLT"]:
            if row[integer_attribute]:
                g.add((starship_uri,sw[integer_attribute],Literal(row[integer_attribute],datatype=XSD.integer)))

        for string_attribute in ["model","manufacturer","consumables","starship_class"]:
            if row[string_attribute]:
                g.add((starship_uri,sw[string_attribute],Literal(row[string_attribute])))

        if row["pilots"]!="None":
            for pilot in row["pilots"].split(", "):
                pilot_uri=URIRef(character_ns[slugify(pilot)])
                g.add((starship_uri,sw.pilot,pilot_uri))
                g.add((pilot_uri,RDF.type,sw.Character))
                g.add((pilot_uri,RDFS.label,Literal(pilot)))

        for film in row["films"].split(", "):
            film_uri=URIRef(film_ns[slugify(film)])
            g.add((starship_uri,sw.appears_in,film_uri))
            g.add((film_uri,RDF.type,sw.Film))
            g.add((film_uri,RDFS.label,Literal(film)))



with open("vehicles.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        vehicle_uri=URIRef(vehicle_ns[slugify(row["name"])])
        g.add((vehicle_uri,RDF.type,sw.Vehicle))
        g.add((vehicle_uri,RDFS.label,Literal(row["name"])))

        for string_attribute in ["model","manufacturer","consumables","vehicle_class"]:
            if row[string_attribute] and row[string_attribute]!="None" and row[string_attribute]!="Unknown":
                g.add((vehicle_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["cost_in_credits","length","max_atmosphering_speed","cargo_capacity"]:
            if row[float_attribute]:
                g.add((vehicle_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for integer_attribute in ["crew","passengers"]:
            if row[integer_attribute]:
                g.add((vehicle_uri,sw[integer_attribute],Literal(row[integer_attribute],datatype=XSD.integer)))

        if row["pilots"]!="None":
            for pilot in row["pilots"].split(", "):
                pilot_uri=URIRef(character_ns[slugify(pilot)])
                g.add((vehicle_uri,sw.pilot,pilot_uri))
                g.add((pilot_uri,RDF.type,sw.Character))
                g.add((pilot_uri,RDFS.label,Literal(pilot)))

        for film in row["films"].split(", "):
            film_uri=URIRef(film_ns[slugify(film)])
            g.add((vehicle_uri,sw.appears_in,film_uri))
            g.add((film_uri,RDF.type,sw.Film))
            g.add((film_uri,RDFS.label,Literal(film)))



with open("weapons.csv","r") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        weapon_uri=URIRef(weapon_ns[slugify(row["name"])])
        g.add((weapon_uri,RDF.type,sw.Weapon))
        g.add((weapon_uri,RDFS.label,Literal(row["name"])))

        for string_attribute in ["model","manufacturer","type","description"]:
            if row[string_attribute]:
                g.add((weapon_uri,sw[string_attribute],Literal(row[string_attribute])))

        for float_attribute in ["cost_in_credits","length"]:
            if row[float_attribute]:
                g.add((weapon_uri,sw[float_attribute],Literal(row[float_attribute],datatype=XSD.float)))

        for film in row["films"].split(", "):
            film_uri=URIRef(film_ns[slugify(film)])
            g.add((weapon_uri,sw.appears_in,film_uri))
            g.add((film_uri,RDF.type,sw.Film))
            g.add((film_uri,RDFS.label,Literal(film)))




rdf_xml=g.serialize(format="xml")

with open("starwars_rdf.xml","w") as f:
    f.write(rdf_xml)



