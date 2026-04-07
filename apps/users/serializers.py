from rest_framework import serializers
from apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'phone_number',
            'age',
            'password',
        ]
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', ''),
            age=validated_data.get('age'),
            password=validated_data['password']
        )
        return user