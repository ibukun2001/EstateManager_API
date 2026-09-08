from django.contrib import admin

from .models import ServiceRequest


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("service_type", "professional_type", "buyer", "status", "preferred_date")
    list_filter = ("service_type", "professional_type", "status")
