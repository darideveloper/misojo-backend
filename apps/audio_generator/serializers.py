from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'id': {
                'read_only': True
            },
            'email': {
                # Validate unique
                'validators': [
                    serializers.UniqueValidator(
                        queryset=User.objects.all(),
                        message='A user with that email already exists.'
                    )
                ],
            }
        }
    
    def create(self, validated_data):
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user