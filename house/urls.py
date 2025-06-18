from django.urls import path
from .views import (
    HouseListView, HouseDetailView, HouseCreateView,
    HouseUpdateView, HouseDeleteView, HouseImageDeleteView
)

urlpatterns = [
    path('houses/', HouseListView.as_view()),
    path('houses/<int:pk>/', HouseDetailView.as_view()),
    path('houses/create/', HouseCreateView.as_view()),
    path('house-images/delete/<int:id>/', HouseImageDeleteView.as_view()),
    path('houses/<int:pk>/edit/', HouseUpdateView.as_view()),
    path('houses/<int:pk>/delete/', HouseDeleteView.as_view()),
]
