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
    path('search', views.search, name='search'),



    path('characters',views.characters, name='characters'),
    path('characters/<str:_id>',views.character_details,name='character_details'),
    path('new/character',views.edit_character,name='new_character'),
    path('characters/<str:_id>/edit',views.edit_character,name='edit_character'),
    path('characters/<str:uri>/delete',views.delete_entity,name='delete_character'),

    path('cities',views.cities,name='cities'),
    path('cities/<str:_id>',views.city_details,name='city_details'),

    path('droids',views.droids,name='droids'),
    path('droids/<str:_id>',views.droid_details,name='droid_details'),

    path('films',views.films,name='films'),
    path('films/<str:_id>',views.film_details,name='film_details'),

    path('music',views.music,name='music'),
    path('music/<str:_id>',views.music_details,name='music_details'),

    path('organisations',views.organizations,name='organizations'),
    path('organisations/<str:_id>',views.organization_details,name='organization_details'),

    path('planets',views.planets,name='planets'),
    path('planets/<str:_id>',views.planet_details,name='planet_details'),

    path('quotes',views.quotes,name='quotes'),
    path('quotes/<str:_id>',views.quote_details,name='quote_details'),

    path('species',views.species,name='species'),
    path('species/<str:_id>',views.specie_details,name='specie_details'),

    path('starships',views.starships,name='starships'),
    path('starships/<str:_id>',views.starship_details,name='starship_details'),

    path('vehicles',views.vehicles,name='vehicles'),
    path('vehicles/<str:_id>',views.vehicle_details,name='vehicle_details'),

    path('weapons',views.weapons,name='weapons'),
    path('weapons/<str:_id>',views.weapon_details,name='weapon_details')
]
