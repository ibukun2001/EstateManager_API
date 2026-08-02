from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Plot
from .serializers import PlotSerializer



class PlotListCreateView(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        plots=Plot.objects.filter(
            estate__company=request.user.company
        )

        serializer=PlotSerializer(
            plots,
            many=True
        )

        return Response(
            serializer.data
        )


    def post(self,request):

        serializer=PlotSerializer(
            data=request.data
        )


        if serializer.is_valid():

            serializer.save()

            return Response(
                serializer.data,
                status=201
            )


        return Response(
            serializer.errors,
            status=400
        )
    

class PlotDetailView(APIView):

    permission_classes=[IsAuthenticated]

    def get(self,request,id):

        try:
            plot=Plot.objects.get(
                id=id,
                estate__company=request.user.company
            )

        except Plot.DoesNotExist:

            return Response(
                {
                    "error":"Plot not found"
                },
                status=404
            )


        serializer=PlotSerializer(plot)

        return Response(serializer.data)


    def delete(self,request,id):

        try:
            plot=Plot.objects.get(
                id=id,
                estate__company=request.user.company
                )

        except Plot.DoesNotExist:

            return Response(
                {
                    "error":"Plot not found"
                },
                status=404
            )


        plot.delete()

        return Response(
            {
                "message":"Plot deleted"
            }
        )

class EstatePlotListView(APIView):

    permission_classes=[IsAuthenticated]

    def get(self,request,estate_id):

        plots=Plot.objects.filter(
            estate_id=estate_id,
            estate__company=request.user.company
        )

        serializer=PlotSerializer(
            plots,
            many=True
        )

        return Response(serializer.data)