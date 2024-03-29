from .models import User
from rest_framework import viewsets
from audio_generator.serializers import UserSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
def get_routes(request):
    routes = [
        '/api/token/',
        '/api/token/refresh/',
        '/api/users/',
        '/api/validate-token/'
    ]
    
    return Response(routes)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenObtainPairView):
    serializer_class = CustomTokenRefreshSerializer


class UserViewSet(viewsets.ModelViewSet):
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'get']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        elif self.request.method == 'GET':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    # No return all registers (return only the user logged in)
    def list(self, request):
        
        user = request.user
        
        return Response({
            'status': 'success',
            'message': 'API.USER.RETRIEVED',
            'data': [
                {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            ]
        })
        
    
class ValidateToken(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        
        return Response({
            'status': 'success',
            'message': 'Token is valid',
            'data': {}
        })