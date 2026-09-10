

from rest_framework import generics, serializers, viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import Board
from .serializers import BoardSerializer, MemberSerializer, TaskSerializer

class BoardsListViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)