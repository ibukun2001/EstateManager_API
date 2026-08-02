from django.urls import path
from .views import EstateListCreateView,CompanyDashboardView, EstateDetailView


urlpatterns=[
    path("",EstateListCreateView.as_view()),
    path("dashboard/",CompanyDashboardView.as_view()),
    path("<int:pk>/",EstateDetailView.as_view()),
]