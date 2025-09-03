from django.urls import path, include
from . import views


#Se define la ruta y nombre para las vistas
urlpatterns = [   
    path('', views.home, name='index'),
]
