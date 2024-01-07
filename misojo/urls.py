from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    
    # Django admin
    path('admin/', admin.site.urls),
    
    # Django REST Framework endpoints
    path('api/', include('audio_generator.urls')),
    
    # redirect home to api
    path('', lambda request: redirect('api/', permanent=False))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)