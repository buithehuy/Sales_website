from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.get_home, name = 'home'),
    path('', include('home.urls')),
]