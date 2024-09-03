from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest

from web.models import Event, EventbriteOrganization, Tag, TechGroup


class TagAdmin(admin.ModelAdmin):
    list_display = ["value"]
    search_fields = ["value"]


class EventAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "date_time",
        "duration",
        "location",
        "group",
        "created_at",
        "updated_at",
    ]
    search_fields = ["id", "name", "duration", "location"]
    list_filter = ["group"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Event]:
        return Event.all.all()


class TechGroupAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "enabled",
        "homepage",
        "created_at",
        "updated_at",
    ]
    search_fields = ["id", "name", "homepage"]
    list_filter = ["enabled"]


# register models
admin.site.register(Event, EventAdmin)
admin.site.register(TechGroup, TechGroupAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(EventbriteOrganization)
