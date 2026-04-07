from rest_framework import serializers
from apps.todo.models import ToDo

class ToDoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.phone_number')
    
    class Meta:
        model = ToDo
        fields = [
            'id',
            'owner',
            'title',
            'description',
            'image',
            'is_completed',
            'created_at',
        ]