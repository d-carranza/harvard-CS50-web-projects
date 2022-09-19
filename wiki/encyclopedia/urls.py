from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # 1- Entry pages
    path("wiki/<str:entry>/", views.entry, name="entry"),
    # 3 - Search
    path("search/", views.search, name="search"),
    # 4 - Create New page
    path("new/", views.new, name="new"),
    # 5 - Edit Page
    path("wiki/<str:entry>/edit/", views.edit, name="edit"),
    # 6 - Redirect
    path("random/", views.randompage, name="random")
]