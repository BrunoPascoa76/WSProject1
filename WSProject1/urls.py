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

    path('characters/',views.characters, name='characters'),
    path('characters/<str:_id>',views.character_details,name='character_details'),
    path('characters/<str:_id>/edit',views.edit_character,name='edit_character'),


    path('planets/<str:_id>',views.planet_details,name='planet_details'),
    path('search',views.search, name='search'),
]
