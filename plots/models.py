from django.db import models
from django.contrib.gis.db import models as gis_models

from estates.models import Estate


class Owner(models.Model):
    full_name = models.CharField(
        max_length=255
    )
    phone = models.CharField(
        max_length=20,
        blank=True
    )
    email = models.EmailField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    def __str__(self):
        return self.full_name


class Plot(gis_models.Model):
    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name="plots"
    )
    owner = models.ForeignKey(
        Owner,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="plots"
    )
    plot_number = models.CharField(
        max_length=30
    )
    block = models.CharField(
        max_length=30
    )
    geometry = gis_models.PolygonField(
        srid=4326,
        spatial_index=True
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    PLOT_TYPES = (
        ("Residential","Residential"),
        ("Commercial","Commercial"),
        ("Infrastructure","Infrastructure"),
    )
    plot_type = models.CharField(
        max_length=30,
        choices=PLOT_TYPES,
        default="Residential"
    )
    STATUS = (
        ("Available","Available"),
        ("Reserved","Reserved"),
        ("Sold","Sold"),
    )
    availability = models.CharField(
        max_length=20,
        choices=STATUS,
        default="Available"
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    class Meta:

        unique_together = (
            "estate",
            "plot_number",
        )

    def __str__(self):
        return self.plot_number