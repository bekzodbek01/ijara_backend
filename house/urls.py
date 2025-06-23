from django.urls import path
from .views import (
    HouseListView, HouseDetailView, HouseCreateView,
    HouseUpdateView, HouseDeleteView, HouseImageDeleteView, HousePublicListView, MyDeactiveHouseListView,
    HousePendingListView, ResendToAdminView, RegionListAPIView, DistrictListByRegionAPIView, ToggleSaveHouseAPIView,
    SavedHouseListAPIView
)

urlpatterns = [
    path('houses/', HouseListView.as_view()),
    path('houses/<int:pk>/', HouseDetailView.as_view()),
    path('houses/create/', HouseCreateView.as_view()),
    path('house-images/delete/<int:id>/', HouseImageDeleteView.as_view()),
    path('houses/<int:pk>/edit/', HouseUpdateView.as_view()),
    path('houses/<int:pk>/delete/', HouseDeleteView.as_view()),


    path('houses/active/', HousePublicListView.as_view(), name='public-houses'),
    path('houses/my-deactive/', MyDeactiveHouseListView.as_view(), name='my-deactive-houses'),
    path('houses/my-pending/', HousePendingListView.as_view(), name='my-pending-houses'),
    path('houses/resend-to-admin/', ResendToAdminView.as_view(), name='resend-to-admin'),

    path('regions/', RegionListAPIView.as_view(), name='region-list'),
    path('districts/by-region/<int:region_id>/', DistrictListByRegionAPIView.as_view(), name='district-by-region'),

    path('houses/<int:pk>/favorite-save/', ToggleSaveHouseAPIView.as_view(), name='toggle-save-house'),
    path('houses/favorite/', SavedHouseListAPIView.as_view(), name='saved-houses'),

]
