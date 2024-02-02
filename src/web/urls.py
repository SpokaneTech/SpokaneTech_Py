from web import views

from django.urls import path

urlpatterns = [
    path("", views.index, name="index"),
    path("events", views.events, name="events"),
]
