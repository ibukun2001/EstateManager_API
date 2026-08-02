from django.urls import path,include
from rest_framework_simplejwt.views import (TokenRefreshView)
from accounts.views import LoginView

urlpatterns = [
    path("login/",LoginView.as_view()),
    path("token/refresh/",TokenRefreshView.as_view()),
]