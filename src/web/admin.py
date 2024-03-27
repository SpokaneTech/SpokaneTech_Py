from django.contrib import admin

from web.models import (Event,
                        TechGroup
                        )


class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'date_time', 'duration', 'location', 'group', 'created_at', 'updated_at']
    search_fields = ['id', 'name', 'duration', 'location']
    list_filter = ['group']


class TechGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'enabled', 'homepage', 'created_at', 'updated_at']
    search_fields = ['id', 'name', 'homepage']
    list_filter = ['enabled']


admin.site.register(Event, EventAdmin)
admin.site.register(TechGroup, TechGroupAdmin)
