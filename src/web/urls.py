from web import views

from django.urls import path

app_name = "web"

urlpatterns = [
    path('', views.Index.as_view(), name="index"),
    path('events', views.ListEvents.as_view(), name="events"),
    path('groups', views.list_tech_groups, name="list_tech_groups"),
    path('groups/<int:pk>', views.get_tech_group, name="get_tech_group"),
    path('events/<int:pk>', views.DetailEvent.as_view(), name="get_event"),
    
    path('sidebar_events', views.GetEvents.as_view(), name="sidebar_events"),
    path('sidebar_groups', views.GetTechGroups.as_view(), name="sidebar_groups"),
]
