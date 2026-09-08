from django.contrib.gis.geos import GEOSException, GEOSGeometry
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from estates.models import Estate

from .models import Owner, Plot
from .serializers import OwnerSerializer, PlotSerializer


class PlotListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plots = Plot.objects.filter(estate__company=request.user.company)
        serializer = PlotSerializer(plots, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        estate_id = data.get("estate")
        estate = get_object_or_404(
            Estate, id=estate_id, company=request.user.company
        )

        geometry_input = data.get("geometry")
        if not geometry_input:
            return Response({"geometry": "This field is required."}, status=400)

        try:
            geometry = GEOSGeometry(geometry_input)
        except (GEOSException, ValueError, TypeError):
            return Response({"geometry": "Invalid geometry."}, status=400)

        data.pop("geometry", None)
        data.pop("estate", None)
        data.pop("owner", None)  # owners are assigned via the allocate endpoint

        serializer = PlotSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        plot = serializer.save(estate=estate, geometry=geometry)
        return Response(PlotSerializer(plot).data, status=201)


class PlotDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        plot = get_object_or_404(
            Plot, id=id, estate__company=request.user.company
        )
        return Response(PlotSerializer(plot).data)

    def patch(self, request, id):
        plot = get_object_or_404(
            Plot, id=id, estate__company=request.user.company
        )
        data = request.data.copy()
        geometry_input = data.pop("geometry", None)

        serializer = PlotSerializer(plot, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        plot = serializer.save()

        if geometry_input:
            try:
                plot.geometry = GEOSGeometry(geometry_input)
                plot.save()
            except (GEOSException, ValueError, TypeError):
                return Response({"geometry": "Invalid geometry."}, status=400)

        return Response(PlotSerializer(plot).data)

    def delete(self, request, id):
        plot = get_object_or_404(
            Plot, id=id, estate__company=request.user.company
        )
        plot.delete()
        return Response({"message": "Plot deleted"})


class EstatePlotListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, estate_id):
        plots = Plot.objects.filter(
            estate_id=estate_id, estate__company=request.user.company
        )
        return Response(PlotSerializer(plots, many=True).data)


class PublicEstatePlotListView(APIView):
    """
    Marketplace plot browsing for a single estate - no auth
    required, owner details are never exposed here.
    """

    permission_classes = [AllowAny]

    def get(self, request, estate_id):
        plots = Plot.objects.filter(estate_id=estate_id)
        data = PlotSerializer(plots, many=True).data
        for plot in data:
            plot.pop("owner", None)
        return Response(data)


class PublicPlotSearchView(APIView):
    """
    Map-based search across every estate at once - powers the
    buyer's "search by map" view. Available plots only, owner
    details stripped, each plot annotated with its estate's name
    and location so the map can label/link back to it.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        plots = Plot.objects.filter(
            availability="Available", estate__status="active"
        ).select_related("estate")

        land_use = request.query_params.get("land_use")
        if land_use:
            plots = plots.filter(plot_type=land_use)

        location = request.query_params.get("location")
        if location:
            plots = plots.filter(estate__location__icontains=location)

        min_size = request.query_params.get("min_size")
        if min_size:
            plots = plots.filter(area__gte=min_size)

        max_size = request.query_params.get("max_size")
        if max_size:
            plots = plots.filter(area__lte=max_size)

        data = PlotSerializer(plots, many=True).data
        for plot, obj in zip(data, plots):
            plot.pop("owner", None)
            plot["estate_name"] = obj.estate.name
            plot["estate_location"] = obj.estate.location

        return Response(data)


class PlotAllocateView(APIView):
    """
    Assigns (or clears) an owner on a plot and updates its
    availability status in one step - what the workspace's
    "Allocate Plot" action calls.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        plot = get_object_or_404(
            Plot, id=id, estate__company=request.user.company
        )

        owner_id = request.data.get("owner_id")
        availability = request.data.get("availability")

        if owner_id:
            owner = get_object_or_404(Owner, id=owner_id)
            plot.owner = owner
        elif owner_id is not None:
            plot.owner = None

        if availability in dict(Plot.STATUS):
            plot.availability = availability

        plot.save()
        return Response(PlotSerializer(plot).data)


class OwnerListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        owners = Owner.objects.filter(
            plots__estate__company=request.user.company
        ).distinct()
        return Response(OwnerSerializer(owners, many=True).data)

    def post(self, request):
        serializer = OwnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
