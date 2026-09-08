from django.urls import path

from .views import ServiceRequestDetailView, ServiceRequestListCreateView

urlpatterns = [
    path("", ServiceRequestListCreateView.as_view()),
    path("<int:id>/", ServiceRequestDetailView.as_view()),
]
