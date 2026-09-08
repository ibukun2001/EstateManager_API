import json

from rest_framework import serializers
from .models import Estate


class EstateSerializer(serializers.ModelSerializer):
    """
    Plain DRF ModelSerializer has no field mapping for GeoDjango
    geometry fields (PointField/PolygonField), so boundary and
    gate_location are declared explicitly and converted to/from
    GeoJSON by hand rather than relying on '__all__' auto-generation.
    They're read-only here; writes happen directly on the model
    instance in the view (see EstateListCreateView.post), the same
    way the shapefile-derived boundary already worked.
    """

    boundary = serializers.SerializerMethodField()
    gate_location = serializers.SerializerMethodField()

    class Meta:
        model = Estate
        fields = "__all__"
        read_only_fields = ["company"]

    def get_boundary(self, obj):
        return json.loads(obj.boundary.geojson) if obj.boundary else None

    def get_gate_location(self, obj):
        return json.loads(obj.gate_location.geojson) if obj.gate_location else None
