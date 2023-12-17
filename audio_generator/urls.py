from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from audio_generator.views import UserViewSet, get_routes
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    
    # Django REST Framework endpoints
    path('', get_routes, name='get_routes'),
    path('', include(router.urls)),
    
    # JWT endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
