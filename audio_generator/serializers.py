from .models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer
)


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
                
        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "password"]
        for field in required_fields:
            if field not in validated_data:
                raise serializers.ValidationError({
                    field: [f"{field} field is required"]
                }, code='required_field')
        
        # Create user and autosent activation email
        user = User.objects.create_user(**validated_data)
        
        return user

    def to_representation(self, instance):
        """ Custom confirmation response """
        return {
            'status': 'success',
            'message': 'User created successfully',
            'data': ""
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    """Customizes JWT default Serializer to add more information about user"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email

        return token

    def validate(self, attrs):
        """ Custom confirmation or error response """

        # Get and validate email and password fields
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        # Check if user exists
        user = User.objects.filter(email=email).first()
        if not user or not user.check_password(password):
            raise serializers.ValidationError({
                "credentials": "invalid user or password"
            }, code='authentication_failed')

        data = super().validate(attrs)

        return {
            "status": "success",
            "message": "Token generated successfully",
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
            return {
                "status": "success",
                "message": "Token refreshed successfully",
                "data": data
            }
        
