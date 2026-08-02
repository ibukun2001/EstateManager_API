from rest_framework import serializers
from .models import Estate


class EstateSerializer(serializers.ModelSerializer):

    class Meta:
        model=Estate
        fields='__all__'
        read_only_fields=["company"]