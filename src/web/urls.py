from django.urls import path, re_path

from web import views

app_name = "web"

urlpatterns = [
    path("", views.GetIndexContent.as_view(), name="default"),
    path("index/", views.GetIndexContent.as_view(), name="index"),
    path("about/", views.GetAboutContent.as_view(), name="about"),
    path("event_calendar/<int:year>/<int:month>/", views.EventCalendarView.as_view(), name="event_calendar"),
    path("techevents/<int:pk>/", views.GetTechEvent.as_view(), name="get_techevent"),
    path("techevents/<int:pk>/details/", views.GetTechEventModal.as_view(), name="techevent_modal"),
    re_path("^techevents/(?P<display>\w+)?/$", views.GetTechEvents.as_view(), name="get_techevents"),
    path("techgroups/<int:pk>/", views.GetTechGroup.as_view(), name="get_techgroup"),
    path("techgroups/<int:pk>/details/", views.GetTechGroupModal.as_view(), name="tech_group_modal"),
    re_path("^techgroups/(?P<display>\w+)?/$", views.GetTechGroups.as_view(), name="get_techgroups"),
]
