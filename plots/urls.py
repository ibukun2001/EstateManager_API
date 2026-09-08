from django.urls import path

from .views import (
    EstatePlotListView,
    OwnerListCreateView,
    PlotAllocateView,
    PlotDetailView,
    PlotListCreateView,
    PublicEstatePlotListView,
    PublicPlotSearchView,
)

urlpatterns = [
    path("", PlotListCreateView.as_view()),
    path("owners/", OwnerListCreateView.as_view()),
    path("public/search/", PublicPlotSearchView.as_view()),
    path("<int:id>/", PlotDetailView.as_view()),
    path("<int:id>/allocate/", PlotAllocateView.as_view()),
    path("estate/<int:estate_id>/", EstatePlotListView.as_view()),
    path("public/estate/<int:estate_id>/", PublicEstatePlotListView.as_view()),
]
