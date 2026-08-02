from django.urls import path

from .views import PlotListCreateView,PlotDetailView,EstatePlotListView



urlpatterns=[
    path("",PlotListCreateView.as_view()),
    path("<int:id>/",PlotDetailView.as_view()),
    path("estate/<int:estate_id>/",EstatePlotListView.as_view()),
]