from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from apps.audio_generator.views import UserViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.shortcuts import redirect

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    
    # Home redirect to api
    path('', lambda request: redirect('api/', permanent=True)),
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # Django REST Framework endpoints
    path('api/', include(router.urls)),
    
    # JWT endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
