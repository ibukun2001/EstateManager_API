from django.db import models

# Create your models here.
from django.db import models
from estates.models import Estate
from plots.models import Plot
from accounts.models import User


class Document(models.Model):
    TYPES = (
        ("Estate Plan","Estate Plan"),
        ("Survey Plan","Survey Plan"),
        ("Receipt","Receipt"),
        ("Deed","Deed"),
        ("Allocation Letter","Allocation Letter"),
        ("Other","Other"),
    )

    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True
    )

    plot = models.ForeignKey(
        Plot,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True
    )

    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="uploaded_documents"
    )

    title = models.CharField(max_length=255)

    document_type = models.CharField(
        max_length=30,
        choices=TYPES,
        default="Other"
    )

    file = models.FileField(
        upload_to="documents/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title