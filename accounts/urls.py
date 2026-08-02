from django.urls import path
from .views import LoginView,CompanyRegisterView,BuyerRegisterView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns=[
    path("login/",LoginView.as_view()),
    path("register/company/",CompanyRegisterView.as_view()),
    path("token/refresh/",TokenRefreshView.as_view()),
    path("register/buyer/",BuyerRegisterView.as_view()),
]