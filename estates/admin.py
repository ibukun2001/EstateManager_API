from django.contrib import admin

from .models import Estate


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "location", "status")
    list_filter = ("status", "company")
    search_fields = ("name", "location")
