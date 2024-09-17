from django.urls import path

from web import views

app_name = "web"

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("set_timezone/", views.set_timezone, name="set_timezone"),
    path("scrape/", views.scrape, name="scrape"),
    path("events", views.ListEvents.as_view(), name="list_events"),
    path("groups", views.ListTechGroup.as_view(), name="list_tech_groups"),
    path("groups/add", views.CreateTechGroup.as_view(), name="add_tech_group"),
    path("groups/<int:pk>", views.DetailTechGroup.as_view(), name="get_tech_group"),
    path("groups/<int:pk>/edit", views.UpdateTechGroup.as_view(), name="edit_tech_group"),
    path("events/add", views.CreateEvent.as_view(), name="add_event"),
    path("events/<int:pk>", views.DetailEvent.as_view(), name="get_event"),
    path("events/<int:pk>/edit", views.UpdateEvent.as_view(), name="update_event"),
    path("build_sidebar", views.BuildSidebar.as_view(), name="build_sidebar"),
    path("events/<int:pk>/details/", views.GetEventDetailsModal.as_view(), name="get_event_details"),
    path("event_calendar/<int:year>/<int:month>/", views.EventCalendarView.as_view(), name="event_calendar"),
    # handyhelpers overrides
    path("filter_list_view", views.FilterListView.as_view(), name="filter_list_view"),
]
