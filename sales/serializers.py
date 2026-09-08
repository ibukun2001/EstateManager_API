from rest_framework import serializers

from plots.serializers import PlotSerializer

from .models import Payment, Purchase, Reservation


class ReservationSerializer(serializers.ModelSerializer):
    plot_detail = PlotSerializer(source="plot", read_only=True)
    buyer_email = serializers.EmailField(source="buyer.email", read_only=True)
    buyer_name = serializers.CharField(source="buyer.first_name", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "buyer",
            "buyer_email",
            "buyer_name",
            "plot",
            "plot_detail",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["buyer", "status"]


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = ["id", "purchase", "reference", "amount", "status", "payment_date"]
        read_only_fields = ["status", "payment_date"]


class PurchaseSerializer(serializers.ModelSerializer):
    plot_detail = PlotSerializer(source="plot", read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    buyer_email = serializers.EmailField(source="buyer.email", read_only=True)
    buyer_name = serializers.CharField(source="buyer.first_name", read_only=True)

    class Meta:
        model = Purchase
        fields = [
            "id",
            "buyer",
            "buyer_email",
            "buyer_name",
            "plot",
            "plot_detail",
            "amount",
            "status",
            "purchased_at",
            "created_at",
            "payments",
        ]
        read_only_fields = ["buyer", "status", "purchased_at"]
