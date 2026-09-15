import json
import os
import tempfile

import geopandas as gpd
from django.contrib.gis.geos import GEOSGeometry, GEOSException, Point
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from plots.models import Owner, Plot

from .models import Estate
from .serializers import EstateSerializer


class EstateListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        estates = Estate.objects.filter(company=request.user.company)
        serializer = EstateSerializer(estates, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()

        latitude = data.get("gate_latitude")
        longitude = data.get("gate_longitude")
        boundary_geojson = data.get("boundary_geojson")

        boundary_file = request.FILES.get("boundary_file")
        plot_file = request.FILES.get("plot_file")

        # Non-model / file fields don't belong in the serializer input.
        for field in (
            "gate_latitude",
            "gate_longitude",
            "boundary_geojson",
            "boundary_file",
            "plot_file",
        ):
            data.pop(field, None)

        serializer = EstateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        estate = serializer.save(company=request.user.company)
        needs_save = False

        # ======================
        # GATE POINT
        # ======================
        if latitude and longitude:
            try:
                estate.gate_location = Point(
                    float(longitude), float(latitude), srid=4326
                )
                needs_save = True
            except (TypeError, ValueError):
                pass

        # ======================
        # BOUNDARY - drawn on the map takes priority over an
        # uploaded file, since it's what the user just interacted with.
        # ======================
        if boundary_geojson:
            try:
                estate.boundary = GEOSGeometry(boundary_geojson)
                needs_save = True
            except (GEOSException, ValueError, TypeError):
                estate.delete()
                return Response(
                    {"boundary": "Invalid boundary geometry."}, status=400
                )
        elif boundary_file:
            try:
                estate.boundary = self.process_boundary(boundary_file)
                needs_save = True
            except Exception as exc:
                estate.delete()
                return Response({"boundary_file": str(exc)}, status=400)

        if needs_save:
            estate.save()

        # ======================
        # PLOTS (optional bulk import from SHP/DWG)
        # ======================
        plot_warning = None
        if plot_file:
            try:
                self.process_plots(plot_file, estate)
            except Exception as exc:
                # The estate itself was created successfully; a bad
                # plot file shouldn't roll that back, just surface it.
                plot_warning = str(exc)

        response_data = EstateSerializer(estate).data
        if plot_warning:
            response_data["plot_import_warning"] = plot_warning

        return Response(response_data, status=201)

    def process_boundary(self, file):
        """
        Read SHP/DWG, reproject to EPSG:4326, return geometry only.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as temp:
            for chunk in file.chunks():
                temp.write(chunk)
            temp_path = temp.name
        try:
            gdf = gpd.read_file(temp_path)
        finally:
            os.remove(temp_path)

        if gdf.crs:
            gdf = gdf.to_crs(epsg=4326)
        else:
            raise Exception("Boundary file has no coordinate reference system.")

        if len(gdf) == 0:
            raise Exception("Boundary file contains no geometry.")

        return GEOSGeometry(gdf.geometry.iloc[0].wkt, srid=4326)

    def process_plots(self, file, estate):
        """
        Read SHP/DWG, reproject to EPSG:4326, create one Plot per
        polygon feature. Attribute columns are matched loosely by
        common naming conventions; anything missing falls back to a
        safe default so the import never hard-fails on a single row.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.name) as temp:
            for chunk in file.chunks():
                temp.write(chunk)
            temp_path = temp.name
        try:
            gdf = gpd.read_file(temp_path)
        finally:
            os.remove(temp_path)

        if gdf.crs:
            gdf = gdf.to_crs(epsg=4326)
        else:
            raise Exception("Plot file has no coordinate reference system.")

        def find_attr(props, *names):
            lowered = {str(k).lower(): v for k, v in props.items()}
            for name in names:
                if name in lowered and lowered[name] not in (None, ""):
                    return lowered[name]
            return None

        created = []
        for index, row in gdf.iterrows():
            geometry = row.geometry
            if geometry is None:
                continue
            if geometry.geom_type == "MultiPolygon":
                geometry = list(geometry.geoms)[0]
            if geometry.geom_type != "Polygon":
                continue

            props = row.to_dict()
            plot_number = find_attr(props, "plot_no", "plot_number", "plotno", "plot") \
                or f"P{index + 1}"
            block = find_attr(props, "block", "blk") or "A"
            area = find_attr(props, "area", "area_sqm", "size") or 0
            price = find_attr(props, "price", "amount", "value") or 0

            plot, _ = Plot.objects.update_or_create(
                estate=estate,
                plot_number=str(plot_number),
                defaults={
                    "block": str(block),
                    "geometry": GEOSGeometry(geometry.wkt, srid=4326),
                    "area": area,
                    "price": price,
                },
            )
            created.append(plot)

        if not created:
            raise Exception("No valid polygon features found in plot file.")

        return created


class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = request.user.company
        estates = Estate.objects.filter(company=company).annotate(
            total_plots=Count("plots"),
            available_plots=Count(
                "plots", filter=Q(plots__availability="Available")
            ),
            sold_plots=Count("plots", filter=Q(plots__availability="Sold")),
            reserved_plots=Count("plots", filter=Q(plots__availability="Reserved")),
        )

        estate_data = [
            {
                "id": estate.id,
                "name": estate.name,
                "location": estate.location,
                "total": estate.total_plots,
                "available": estate.available_plots,
                "sold": estate.sold_plots,
                "reserved": estate.reserved_plots,
            }
            for estate in estates
        ]

        total_plots = sum(e["total"] for e in estate_data)
        available_plots = sum(e["available"] for e in estate_data)
        sold_plots = sum(e["sold"] for e in estate_data)

        return Response(
            {
                "company": company.name,
                "kpis": [
                    {
                        "title": "Total Estates",
                        "value": estates.count(),
                        "color": "#2563eb",
                    },
                    {
                        "title": "Total Plots",
                        "value": total_plots,
                        "color": "#2563eb",
                    },
                    {
                        "title": "Available Plots",
                        "value": available_plots,
                        "color": "#16a34a",
                    },
                    {
                        "title": "Sold Plots",
                        "value": sold_plots,
                        "color": "#dc2626",
                    },
                ],
                "estates": estate_data,
                "activities": [],
            }
        )


class EstateDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        estate = get_object_or_404(Estate, pk=pk, company=request.user.company)
        serializer = EstateSerializer(estate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        estate = get_object_or_404(Estate, pk=pk, company=request.user.company)

        data = request.data.copy()
        latitude = data.pop("gate_latitude", None)
        longitude = data.pop("gate_longitude", None)

        serializer = EstateSerializer(estate, data=data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        estate = serializer.save()

        if latitude and longitude:
            try:
                estate.gate_location = Point(float(longitude), float(latitude), srid=4326)
                estate.save()
            except (TypeError, ValueError):
                pass

        return Response(EstateSerializer(estate).data)

    def delete(self, request, pk):
        estate = get_object_or_404(Estate, pk=pk, company=request.user.company)
        estate.delete()
        return Response(status=204)


class PublicEstateListView(APIView):
    """
    Marketplace browsing - every estate across every company, with
    live plot-availability counts, no auth required.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        estates = Estate.objects.filter(status="active").select_related("company").annotate(
            total_plots=Count("plots"),
            available_plots=Count(
                "plots", filter=Q(plots__availability="Available")
            ),
        )

        search = request.query_params.get("search")
        if search:
            estates = estates.filter(
                Q(name__icontains=search) | Q(location__icontains=search)
            )

        location = request.query_params.get("location")
        if location:
            estates = estates.filter(location__icontains=location)

        land_use = request.query_params.get("land_use")
        if land_use:
            estates = estates.filter(plots__plot_type=land_use)

        min_size = request.query_params.get("min_size")
        if min_size:
            estates = estates.filter(plots__area__gte=min_size)

        max_size = request.query_params.get("max_size")
        if max_size:
            estates = estates.filter(plots__area__lte=max_size)

        estates = estates.distinct()

        return Response(
            [
                {
                    "id": estate.id,
                    "name": estate.name,
                    "location": estate.location,
                    "description": estate.description,
                    "company": estate.company.name,
                    "company_website": estate.company.website,
                    "image": estate.image.url if estate.image else None,
                    "total_plots": estate.total_plots,
                    "available_plots": estate.available_plots,
                }
                for estate in estates
            ]
        )


class PublicEstateDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        estate = get_object_or_404(Estate, pk=pk)
        data = EstateSerializer(estate).data
        data["company"] = estate.company.name
        data["company_website"] = estate.company.website
        return Response(data)
