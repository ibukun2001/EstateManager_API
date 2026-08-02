from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Estate
from .serializers import EstateSerializer

from django.contrib.gis.geos import Point
from rest_framework.parsers import MultiPartParser, FormParser

import geopandas as gpd
import tempfile
import os

from rest_framework import status
from django.shortcuts import get_object_or_404



class EstateListCreateView(APIView):
    permission_classes=[
        IsAuthenticated
    ]
    def get(self,request):
        estates=Estate.objects.filter(
            company=request.user.company
        )
        serializer=EstateSerializer(
            estates,
            many=True
        )
        return Response(
            serializer.data
        )
    def post(self,request):
        serializer=EstateSerializer(
            data=request.data
        )
        if serializer.is_valid():
            serializer.save(
                company=request.user.company
            )
            return Response(
                serializer.data,
                status=201
            )
        return Response(
            serializer.errors,
            status=400
        )





class EstateListCreateView(APIView):
    permission_classes=[
        IsAuthenticated
    ]
    parser_classes=[
        MultiPartParser,
        FormParser
    ]
    def get(self,request):
        estates=Estate.objects.filter(
            company=request.user.company
        )
        serializer=EstateSerializer(
            estates,
            many=True
        )
        return Response(serializer.data)
    def post(self,request):
        data=request.data.copy()
        # ======================
        # CREATE GATE POINT
        # ======================
        latitude=data.get(
            "gate_latitude"
        )
        longitude=data.get(
            "gate_longitude"
        )
        if latitude and longitude:
            data["gate_location"] = Point(
                float(longitude),
                float(latitude),
                srid=4326
            )
        # ======================
        # REMOVE FILE FIELDS
        # ======================
        boundary_file=request.FILES.get(
            "boundary_file"
        )
        plot_file=request.FILES.get(
            "plot_file"
        )
        data.pop(
            "boundary_file",
            None
        )
        data.pop(
            "plot_file",
            None
        )
        serializer=EstateSerializer(
            data=data
        )
        if serializer.is_valid():
            estate=serializer.save(
                company=request.user.company
            )
            # ======================
            # PROCESS BOUNDARY
            # ======================
            if boundary_file:
                geometry=self.process_boundary(
                    boundary_file
                )
                estate.boundary=geometry
                estate.save()
            return Response(
                EstateSerializer(estate).data,
                status=201
            )
        return Response(
            serializer.errors,
            status=400
        )
    def process_boundary(self,file):
        """
        Read SHP/DWG
        Convert CRS to 4326
        Return geometry only
        """
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file.name
        ) as temp:
            for chunk in file.chunks():
                temp.write(chunk)
            temp_path=temp.name
        gdf=gpd.read_file(
            temp_path
        )
        os.remove(
            temp_path
        )
        # Convert CRS
        if gdf.crs:
            gdf=gdf.to_crs(
                epsg=4326
            )
        else:
            raise Exception(
                "File has no CRS"
            )
        # Get geometry only
        geometry=gdf.geometry.iloc[0]
        return geometry


class CompanyDashboardView(APIView):
    permission_classes=[
        IsAuthenticated
    ]
    def get(self,request):
        company=request.user.company
        estates=Estate.objects.filter(
            company=company
        )
        estate_data=[]
        for estate in estates:
            estate_data.append({
                "id":estate.id,
                "name":estate.name,
                "location":estate.location,
                "total":0,
                "available":0,
                "sold":0
            })
        return Response({
            "company":company.name,
            "kpis":[
                {
                    "title":"Total Estates",
                    "value":estates.count(),
                    "color":"#2563eb"
                },
                {
                    "title":"Total Plots",
                    "value":0,
                    "color":"#2563eb"
                },
                {
                    "title":"Available Plots",
                    "value":0,
                    "color":"#16a34a"
                },
                {
                    "title":"Sold Plots",
                    "value":0,
                    "color":"#dc2626"
                }
            ],
            "estates":estate_data,

            "activities":[]
        })

class EstateDetailView(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,pk):
        estate=get_object_or_404(
            Estate,
            pk=pk,
            company=request.user.company
        )

        serializer=EstateSerializer(estate)

        return Response(serializer.data,status=status.HTTP_200_OK)