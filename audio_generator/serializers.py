from .models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer
)
from rest_framework_simplejwt.tokens import Token

class UserSerializer(serializers.HyperlinkedModelSerializer):
    """ User custom crate and representation serializer """

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        """ Validate required fields and password length after create user"""
            
        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "password"]
        for field in required_fields:
            if field not in validated_data:
                raise serializers.ValidationError({
                    field: [f"{field} is required"]
                }, code='required_field')
                
        # Validate password length
        if len(validated_data['password']) < 8:
            raise serializers.ValidationError({
                "password": "REGISTER.INVALID_PASSWORD"
            }, code='invalid_password')
        
        # Create user and autosent activation email
        user = User.objects.create_user(**validated_data)
        return user
    
    def to_representation(self, instance):
        """ Custom response when user is created """
        return {
            "status": "success",
            "message": "REGISTER.CREATED",
            "data": {}
        }
        

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """ Custom token validation and response """

    @classmethod
    def get_token(cls, user: User) -> Token:
        """ Add email to token payload
        
        Args:
            user (User): User object
            
        Returns:
            Token: JWT token
        """
    
        token = super().get_token(user)
        token['email'] = user.email

        # Token with user information
        return token

    def validate(self, attrs):
        """ Custom validation: credentials, activation and valid response """

        # Get and validate email and password fields
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        
        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            
            raise serializers.ValidationError({
                "credentials": "TOKEN.INVALID_CRED"
            }, code='authentication_failed')
            
        # Error if user is not active
        if not user.is_active:
            
            raise serializers.ValidationError({
                "activation": "TOKEN.INACTIVE"
            }, code='user_not_active')

        data = super().validate(attrs)

        # Json response
        return {
            "status": "success",
            "message": "TOKEN.GENERATED",
            "data": data
        }


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """ Custom token refresh validation and response """
    
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
                "message": "Token refreshed successfully",
                "data": data
            }