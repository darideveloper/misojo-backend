from .models import User
from rest_framework import viewsets
from audio_generator.serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def get_routes(request):
    routes = [
        '/api/token/',
        '/api/token/refresh/',
    ]
    
    return Response(routes)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post']