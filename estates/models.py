from django.db import models


from django.contrib.gis.db import models as gis_models
from accounts.models import Company


class Estate(gis_models.Model):
    STATUS_CHOICES=(
        ("active","Active"),
        ("inactive","Inactive"),
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="estates"
    )
    name = models.CharField(
        max_length=255
    )
    location = models.CharField(
        max_length=255,
        blank=True
    )
    description = models.TextField(
        blank=True
    )
    image = models.ImageField(
        upload_to="estate_images/",
        null=True,
        blank=True
    )
    gate_location = gis_models.PointField(
        srid=4326,
        null=True,
        blank=True
    )
    boundary = gis_models.PolygonField(
        srid=4326,
        spatial_index=True,
        null=True,
        blank=True,
    )
    status=models.CharField(
            max_length=20,
            choices=STATUS_CHOICES,
            default="active"
        )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at=models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name