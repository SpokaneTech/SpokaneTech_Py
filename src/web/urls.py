from web import views

from django.urls import path

app_name = "web"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("events", views.ListEvents.as_view(), name="events"),
    path("groups", views.list_tech_groups, name="list_tech_groups"),
    path("groups/<int:pk>", views.DetailTechGroup.as_view(), name="get_tech_group"),
    path("events/<int:pk>", views.DetailEvent.as_view(), name="get_event"),
    path("build_sidebar", views.BuildSidebar.as_view(), name="build_sidebar"),
    path("events/<int:pk>/details/", views.GetEventDetailsModal.as_view(), name="get_event_details"),
    path("event_calendar/<int:year>/<int:month>/", views.EventCalendarView.as_view(), name="event_calendar"),
]
