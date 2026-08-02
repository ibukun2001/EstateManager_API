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
                company=company
            )

            refresh=RefreshToken.for_user(user)

            return Response({
                "refresh":str(refresh),
                "access":str(refresh.access_token),
                "role":user.role
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
            role="buyer"
        )
        refresh=RefreshToken.for_user(user)
        return Response({
            "refresh":str(refresh),
            "access":str(refresh.access_token),
            "role":user.role
        },status=201)