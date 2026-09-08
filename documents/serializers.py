from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(
        source="uploaded_by.email", read_only=True
    )

    class Meta:
        model = Document
        fields = [
            "id",
            "estate",
            "plot",
            "uploaded_by",
            "uploaded_by_email",
            "title",
            "document_type",
            "file",
            "created_at",
        ]
        read_only_fields = ["uploaded_by"]
