from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer


class DocumentListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        user = request.user
        documents = Document.objects.filter(
            estate__company=user.company
        ) | Document.objects.filter(plot__estate__company=user.company)

        estate_id = request.query_params.get("estate")
        if estate_id:
            documents = documents.filter(estate_id=estate_id)

        plot_id = request.query_params.get("plot")
        if plot_id:
            documents = documents.filter(plot_id=plot_id)

        return Response(DocumentSerializer(documents.distinct(), many=True).data)

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
