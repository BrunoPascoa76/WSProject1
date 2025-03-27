"""
URL configuration for WSProject1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path
from StarwarsRDS import views
from django.conf.urls import handler404

handler404 = views.handle_404_error
urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('characters', views.character_list, name='character_list'),
     path('edit/attributes/<path:uri>/', views.edit_character_attributes, name='edit_character_attributes'),
    path('edit/relations/<path:uri>/', views.edit_character_relations, name='edit_character_relations'),
    path('characters/<path:uri>', views.character_details , name='character_details'),
    path('films',views.getAllFilms, name='films'),
    path('droids',views.getAllDroids, name='droids'),
    path('cities',views.getAllCities, name='cities'),
    path('music',views.getAllMusic, name='music'),
    path('organizations',views.getAllOrganizations, name='organizations'),
    path('planets',views.getAllPlanets, name='planets'),
    path('quotes',views.getAllQuotes, name='quotes'),
    path('species',views.getAllSpecies, name='species'),
    path('starships',views.getAllStarships, name='starships'),
    path('vehicles',views.getAllVehicles, name='vehicles'),
    path('weapons',views.getAllWeapons, name='weapons'),
    path('character/delete/<path:uri>/', views.delete_character, name='delete_character'),
    path('cities/<path:uri>', views.city_details, name='city_details'),
    path('droids/<path:uri>', views.droid_details, name='droid_details'),
    path('films/<path:uri>', views.film_details, name='film_details'),
    path('music/<path:uri>', views.music_details, name='music_details'),
    path('organizations/<path:uri>', views.organization_details, name='organization_details'),
    path('planets/<path:uri>', views.planet_details, name='planet_details'),
    path('quotes/<path:uri>', views.quote_details, name='quote_details'),
    path('species/<path:uri>', views.specie_details, name='species_details'),
    path('starships/<path:uri>', views.starship_details, name='starship_details'),
    path('vehicles/<path:uri>', views.vehicle_details, name='vehicle_details'),
    path('weapons/<path:uri>', views.weapon_details, name='weapon_details'),


    path('search',views.search, name='search'),
    path('<str:_type>/',views.type_graph, name='description'),
]
