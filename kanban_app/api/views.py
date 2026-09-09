

from rest_framework import generics, serializers
from ..models import Board

class BoardsListView(generics.ListAPIView):
    queryset = Board.objects.all()
    serializer_class = 'BoardSerializer'

class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']