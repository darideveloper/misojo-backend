from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # Django REST Framework endpoints
    path('api/', include('audio_generator.urls')),
    
    # redirect home to api
    path('', lambda request: redirect('api/', permanent=False)),
]
