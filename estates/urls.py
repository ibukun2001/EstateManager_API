from django.urls import path

from .views import (
    CompanyDashboardView,
    EstateDetailView,
    EstateListCreateView,
    PublicEstateDetailView,
    PublicEstateListView,
)

urlpatterns = [
    path("", EstateListCreateView.as_view()),
    path("dashboard/", CompanyDashboardView.as_view()),
    path("public/", PublicEstateListView.as_view()),
    path("public/<int:pk>/", PublicEstateDetailView.as_view()),
    path("<int:pk>/", EstateDetailView.as_view()),
]
