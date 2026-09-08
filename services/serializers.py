from rest_framework import serializers

from plots.serializers import PlotSerializer

from .models import ServiceRequest


class ServiceRequestSerializer(serializers.ModelSerializer):
    plot_detail = PlotSerializer(source="plot", read_only=True)
    estate_name = serializers.CharField(source="estate.name", read_only=True)
    buyer_email = serializers.EmailField(source="buyer.email", read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            "id",
            "buyer",
            "buyer_email",
            "plot",
            "plot_detail",
            "estate",
            "estate_name",
            "service_type",
            "professional_type",
            "preferred_date",
            "notes",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["buyer", "status"]
