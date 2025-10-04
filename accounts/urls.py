from django.urls import path
from .views import contestants_view
from .views import signin_view, signup_view
from .views import howitworks_view, finaleroyale_view
from .views import home_view, arenas_view, profile_view

urlpatterns = [
    path("", home_view, name="home"),
    path("arenas", arenas_view, name="arenas"),
    path("contestants", contestants_view, name="contestants"),
    path("how-it-works", howitworks_view, name="howitworks"),
    path("finale-royale", finaleroyale_view, name="finaleroyale"),
    path("login", signin_view, name="login"),
    path("signup", signup_view, name="signup"),
    path("profile", profile_view, name="profile")
]
