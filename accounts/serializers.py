from rest_framework import serializers
from .models import User,Company


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model=Company
        fields=[
            "id",
            "name",
            "slug",
            "email",
            "phone",
            "address",
            "website"
        ]


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=User
        fields=[
            "id",
            "username",
            "email",
            "phone",
            "role",
            "company"
        ]