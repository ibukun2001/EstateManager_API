from django.conf import settings
from django.db import models

from estates.models import Estate
from plots.models import Plot


class ServiceRequest(models.Model):
    """
    A buyer asking a professional (surveyor, lawyer, architect,
    builder) to do something in relation to a plot or estate -
    a land survey, deed of assignment, construction consultation,
    or a general appointment.
    """

    SERVICE_TYPES = [
        ("Land Survey", "Land Survey"),
        ("Drone Survey", "Drone Survey"),
        ("GIS Mapping", "GIS Mapping"),
        ("Valuation", "Valuation"),
        ("Deed of Assignment", "Deed of Assignment"),
        ("Construction", "Construction"),
        ("Appointment", "Appointment"),
    ]

    PROFESSIONAL_TYPES = [
        ("Surveyor", "Surveyor"),
        ("Lawyer", "Lawyer"),
        ("Architect", "Architect"),
        ("Builder", "Builder"),
        ("Valuer", "Valuer"),
    ]

    STATUS = [
        ("Pending", "Pending"),
        ("Scheduled", "Scheduled"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_requests",
    )
    plot = models.ForeignKey(
        Plot, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_requests"
    )
    estate = models.ForeignKey(
        Estate, on_delete=models.SET_NULL, null=True, blank=True, related_name="service_requests"
    )

    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    professional_type = models.CharField(max_length=20, choices=PROFESSIONAL_TYPES)

    preferred_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_type} ({self.professional_type}) - {self.buyer}"
