from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from plots.models import Plot

from .models import Purchase, Reservation
from .serializers import PurchaseSerializer, ReservationSerializer


class ReservationListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "buyer":
            reservations = Reservation.objects.filter(buyer=user)
        else:
            reservations = Reservation.objects.filter(
                plot__estate__company=user.company
            )
        return Response(ReservationSerializer(reservations, many=True).data)

    def post(self, request):
        if request.user.role != "buyer":
            return Response(
                {"error": "Only buyers can reserve a plot."}, status=403
            )

        plot_id = request.data.get("plot")
        plot = get_object_or_404(Plot, id=plot_id)

        if plot.availability != "Available":
            return Response(
                {"error": "This plot is not available for reservation."},
                status=400,
            )

        reservation = Reservation.objects.create(buyer=request.user, plot=plot)
        plot.availability = "Reserved"
        plot.save()

        return Response(ReservationSerializer(reservation).data, status=201)


class ReservationActionView(APIView):
    """
    PATCH { "action": "approve" | "cancel" }
    Approving is company-only. Cancelling can be done by either the
    buyer who made the reservation or the owning company, and always
    frees the plot back up.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        reservation = get_object_or_404(Reservation, id=id)
        user = request.user
        is_owning_company = (
            user.role == "company"
            and reservation.plot.estate.company_id == user.company_id
        )
        is_buyer = user.role == "buyer" and reservation.buyer_id == user.id

        action = request.data.get("action")

        if action == "approve":
            if not is_owning_company:
                return Response({"error": "Not authorized."}, status=403)
            reservation.status = "Approved"
            reservation.save()

        elif action == "cancel":
            if not (is_owning_company or is_buyer):
                return Response({"error": "Not authorized."}, status=403)
            reservation.status = "Cancelled"
            reservation.save()
            reservation.plot.availability = "Available"
            reservation.plot.save()

        else:
            return Response({"error": "Unknown action."}, status=400)

        return Response(ReservationSerializer(reservation).data)


class PurchaseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "buyer":
            purchases = Purchase.objects.filter(buyer=user)
        else:
            purchases = Purchase.objects.filter(
                plot__estate__company=user.company
            )
        return Response(PurchaseSerializer(purchases, many=True).data)

    def post(self, request):
        """
        Company finalizes a sale on a reserved/approved plot for a
        given buyer. This is deliberately simple - it doesn't touch
        payment processing, just books the sale and marks the plot sold.
        """
        if request.user.role != "company":
            return Response(
                {"error": "Only the owning company can record a sale."},
                status=403,
            )

        plot_id = request.data.get("plot")
        buyer_id = request.data.get("buyer")
        amount = request.data.get("amount")

        plot = get_object_or_404(
            Plot, id=plot_id, estate__company=request.user.company
        )

        if hasattr(plot, "purchase"):
            return Response({"error": "This plot has already been sold."}, status=400)

        from accounts.models import User

        buyer = get_object_or_404(User, id=buyer_id, role="buyer")

        from django.utils import timezone

        purchase = Purchase.objects.create(
            buyer=buyer,
            plot=plot,
            amount=amount or plot.price,
            status="Completed",
            purchased_at=timezone.now(),
        )
        plot.availability = "Sold"
        plot.save()

        return Response(PurchaseSerializer(purchase).data, status=201)
