
from django.urls import path

from . import views

urlpatterns = [
    # Main routes
    path("home", views.home, name="home"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),

    # API routes
    path("follow", views.follow, name="follow"),
    path("edit", views.edit, name="edit"),
    path("like", views.like, name="like"),
    path("unlike", views.unlike, name="unlike"),
    
    # User management routes
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register")
]
