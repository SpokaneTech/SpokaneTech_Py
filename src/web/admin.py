from django.contrib import admin

# import models
from web.models import Event, TechGroup


class EventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "description",
        "date_time",
        "duration",
        "location",
        "group",
        "approved",
        "created_at",
        "updated_at",
    ]
    search_fields = ["id", "name", "description", "duration", "location"]
    list_filter = ["group", "approved"]


class TechGroupAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "description", "enabled", "homepage", "created_at", "updated_at"]
    search_fields = ["id", "name", "description", "homepage"]
    list_filter = ["enabled"]


# register models
admin.site.register(Event, EventAdmin)
admin.site.register(TechGroup, TechGroupAdmin)
