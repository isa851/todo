from rest_framework import viewsets, mixins, permissions
from .models import User
from .serializers import UserSerializer

# Create your views here.

class UserRegistrationViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]