from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='listings'), #this goes to /listings because its in the listings app urls
    path('<int:listing_id>', views.listing, name='listing'), # u identify the type of the parameter: <int> and then how u want to call it: listing_id
    path('search', views.search, name='search') #this will go to a method called views.search
]
#the reason when u dont use for example listings/search, is because u are going to link it to the main urls.py where
#u will tell that anything that has listings/ should look into this file
