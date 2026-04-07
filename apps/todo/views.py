from rest_framework import viewsets, permissions, filters
from .models import ToDo
from .serializers import ToDoSerializer

# Create your views here.

class ToDoViewSet(viewsets.ModelViewSet):
    serializer_class = ToDoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def get_queryset(self):
        return ToDo.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)