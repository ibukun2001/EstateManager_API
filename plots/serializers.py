import json

from rest_framework import serializers
from .models import Owner, Plot


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Owner
        fields = ["id", "full_name", "phone", "email"]


class PlotSerializer(serializers.ModelSerializer):
    # Same reasoning as EstateSerializer.boundary: plain DRF has no
    # field mapping for GeoDjango PolygonField, so it's declared
    # explicitly and converted to GeoJSON by hand.
    geometry = serializers.SerializerMethodField()
    owner = OwnerSerializer(read_only=True)

    class Meta:
        model = Plot
        fields = [
            "id",
            "estate",
            "owner",
            "plot_number",
            "block",
            "geometry",
            "area",
            "price",
            "description",
            "plot_type",
            "availability",
            "created_at",
        ]
        read_only_fields = ["estate"]

    def get_geometry(self, obj):
        return json.loads(obj.geometry.geojson) if obj.geometry else None
