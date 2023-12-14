from django.contrib.auth.models import User
from rest_framework import viewsets
from apps.audio_generator.serializers import UserSerializer
from django.shortcuts import render
from rest_framework.permissions import AllowAny


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']


def test_view(request):
    # Your view logic here
    return render(request, 'audio_generator/index.html')