from .models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer
)
from django.utils.translation import gettext as _


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        """ Custom create method to hash password """
                
        # Get languaje from request
        lang = self.context['request'].headers.get('Accept-Language', 'en')
        
        # Generate internationalized errors
        if lang == 'es':
            error_required_field = "es requerido/a"
            error_password = "la contraseña debe tener al menos 8 caracteres"
        else:
            error_required_field = "is required"
            error_password = "password must be at least 8 characters"
            
        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "password"]
        for field in required_fields:
            if field not in validated_data:
                raise serializers.ValidationError({
                    field: [f"{field} {error_required_field}"]
                }, code='required_field')
                
        # Validate password length
        if len(validated_data['password']) < 8:
            raise serializers.ValidationError({
                field: [error_password]
            }, code='password_length')
        
        # Create user and autosent activation email
        User.objects.create_user(**validated_data)
        
        # Generate internationalized message
        if lang == 'es':
            message = "Usuario creado correctamente"
        else:
            message = "User created successfully"
        
        # Json response
        return {
            'status': 'success',
            'message': message,
            'data': {}
        }
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Customizes JWT default Serializer to add more information about user"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email

        # Token with user information
        return token

    def validate(self, attrs):
        """ Custom confirmation or error response """

        # Get and validate email and password fields
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # Get languaje from request
        lang = self.context['request'].headers.get('Accept-Language', 'en')
        
        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            
            # Generate internationalized message
            if lang == 'es':
                message = "Usuario o contraseña incorrectos"
            else:
                message = "Invalid user or password"
            
            raise serializers.ValidationError({
                "credentials": message
            }, code='authentication_failed')
            
        # Error if user is not active
        if not user.is_active:
            
            # Generate internationalized message
            if lang == 'es':
                message = "Usuario no activo. Revisa tu correo para activar tu cuenta"
            else:
                message = "User not active. Check your email to activate your account"
            
            raise serializers.ValidationError({
                "activation": message
            }, code='user_not_active')

        data = super().validate(attrs)
        
        if lang == 'es':
            message = "Welcome to Misojo"
        else:
            message = "Bienvenido a Misojo"
        
        # Json response
        return {
            "status": "success",
            "message": message,
            "data": data
        }


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        """ Custom confirmation or error response """
        
        try:
            data = super().validate(attrs)
        except serializers.ValidationError:
            raise serializers.ValidationError({
                "token": "Token is invalid or expired"
            }, code='token_not_valid')
        else:
            # Json response
            return {
                "status": "success",
                "message": _("Token refreshed successfully"),
                "data": data
            }