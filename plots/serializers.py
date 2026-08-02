from rest_framework import serializers
from .models import Plot,Owner


class OwnerSerializer(serializers.ModelSerializer):

    class Meta:
        model=Owner
        fields=[
            "id",
            "full_name",
            "phone",
            "email"
        ]



class PlotSerializer(serializers.ModelSerializer):

    class Meta:
        model=Plot
        fields=[
            "id",
            "estate",
            "owner",
            "plot_number",
            "block",
            "geometry",
            "area",
            "price",
            "plot_type",
            "availability",
            "created_at"
        ]