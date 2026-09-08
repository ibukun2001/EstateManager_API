from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ServiceRequest
from .serializers import ServiceRequestSerializer


class ServiceRequestListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == "buyer":
            requests = ServiceRequest.objects.filter(buyer=user)
        else:
            requests = ServiceRequest.objects.filter(
                estate__company=user.company
            ) | ServiceRequest.objects.filter(
                plot__estate__company=user.company
            )
            requests = requests.distinct()
        return Response(
            ServiceRequestSerializer(requests.order_by("-created_at"), many=True).data
        )

    def post(self, request):
        if request.user.role != "buyer":
            return Response(
                {"error": "Only buyers can submit a service request."}, status=403
            )

        serializer = ServiceRequestSerializer(data=request.data)
        if serializer.is_valid():
            service_request = serializer.save(buyer=request.user)
            return Response(
                ServiceRequestSerializer(service_request).data, status=201
            )
        return Response(serializer.errors, status=400)


class ServiceRequestDetailView(APIView):
    """
    PATCH is used by the owning company to move a request through its
    lifecycle (Pending -> Scheduled -> Completed, or Cancelled), and
    by the buyer to cancel their own request.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        service_request = get_object_or_404(ServiceRequest, id=id)
        user = request.user

        is_owning_company = user.role == "company" and (
            (service_request.estate and service_request.estate.company_id == user.company_id)
            or (
                service_request.plot
                and service_request.plot.estate.company_id == user.company_id
            )
        )
        is_requesting_buyer = user.role == "buyer" and service_request.buyer_id == user.id

        status_value = request.data.get("status")

        if status_value == "Cancelled":
            if not (is_owning_company or is_requesting_buyer):
                return Response({"error": "Not authorized."}, status=403)
        elif not is_owning_company:
            return Response({"error": "Not authorized."}, status=403)

        if status_value in dict(ServiceRequest.STATUS):
            service_request.status = status_value

        preferred_date = request.data.get("preferred_date")
        if preferred_date and is_owning_company:
            service_request.preferred_date = preferred_date

        service_request.save()
        return Response(ServiceRequestSerializer(service_request).data)
