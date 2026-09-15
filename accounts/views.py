from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

from .models import User,Company
from .serializers import UserSerializer,CompanySerializer
from rest_framework import status

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self,request):
        email=request.data.get("email")
        password=request.data.get("password")
        user=authenticate(
            request,
            email=email,
            password=password
        )

        if user:

            refresh=RefreshToken.for_user(user)

            return Response({
                "refresh":str(refresh),
                "access":str(refresh.access_token),
                "role":user.role,
                "email":user.email,
                "name":user.first_name,
                "company_slug":user.company.slug if user.company else None,
                "company_name":user.company.name if user.company else None,
            })

        return Response(
            {
                "error":"Invalid credentials"
            },
            status=400
        )
    
class CompanyRegisterView(APIView):

    authentication_classes=[]
    permission_classes=[]

    def post(self,request):

        company_data={
            "name":request.data.get("company_name"),
            "email":request.data.get("company_email"),
            "phone":request.data.get("company_phone"),
            "address":request.data.get("company_address")
        }

        company_serializer=CompanySerializer(
            data=company_data
        )

        if company_serializer.is_valid():

            company=company_serializer.save()

            user=User.objects.create_user(
                email=request.data.get("email"),
                password=request.data.get("password"),
                role="company",
                company=company,
                first_name=request.data.get("name","")
            )

            refresh=RefreshToken.for_user(user)

            return Response({
                "refresh":str(refresh),
                "access":str(refresh.access_token),
                "role":user.role,
                "email":user.email,
                "name":user.first_name,
                "company_slug":company.slug,
                "company_name":company.name,
            },status=201)


        return Response(
            company_serializer.errors,
            status=400
        )
    

class BuyerRegisterView(APIView):

    permission_classes=[AllowAny]

    def post(self,request):

        user=User.objects.create_user(
            email=request.data.get("email"),
            password=request.data.get("password"),
            role="buyer",
            first_name=request.data.get("name","")
        )
        refresh=RefreshToken.for_user(user)
        return Response({
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "role":user.role,
            "email":user.email,
            "name":user.first_name,
        },status=201)