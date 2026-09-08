from django.contrib import admin

from .models import Owner, Plot


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone", "email")
    search_fields = ("full_name", "phone", "email")


@admin.register(Plot)
class PlotAdmin(admin.ModelAdmin):
    list_display = ("plot_number", "estate", "block", "availability", "price")
    list_filter = ("availability", "plot_type", "estate")
    search_fields = ("plot_number", "block")
