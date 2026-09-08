from django.urls import path

from .views import (
    PurchaseListCreateView,
    ReservationActionView,
    ReservationListCreateView,
)

urlpatterns = [
    path("reservations/", ReservationListCreateView.as_view()),
    path("reservations/<int:id>/", ReservationActionView.as_view()),
    path("purchases/", PurchaseListCreateView.as_view()),
]
