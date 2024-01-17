from web import views

from django.urls import path

urlpatterns = [
    path('', views.index, name="index"),
    path('events', views.events, name="events"),
    path('groups', views.list_tech_groups, name="techgroups"),
]
