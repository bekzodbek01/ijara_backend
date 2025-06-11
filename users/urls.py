from django.urls import path
from .views import FaceCompareAPIView, UserRegistrationView, UserLoginView, UserPasswordChangeView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('change-password/', UserPasswordChangeView.as_view(), name='user-change-password'),
    path('face-compare/', FaceCompareAPIView.as_view(), name='face-compare'),
    path('face-compare/', FaceCompareAPIView.as_view(), name='face-compare'),
]
