
from django.db.models import Q
from rest_framework import generics, serializers, viewsets
from .permissions import IsOwnerOrMember
from rest_framework.permissions import IsAuthenticated
from ..models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer

class BoardsListViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrMember]
    
    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members__user=user)).distinct()
    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'destroy', 'partial_update']:
            return BoardDetailSerializer
        return BoardListSerializer

# class BoardsDetailViewSet(viewsets.ModelViewSet):
#     queryset = Board.objects.all()
#     serializer_class = BoardDetailSerializer
#     permission_classes = [IsAuthenticated, IsOwnerOrMember]

#     def perform_create(self, serializer):
#         serializer.save(owner_id=self.request.user.id)

#     def get_queryset(self):
#         user = self.request.user
#         return Board.objects.filter(Q(owner=user) | Q(members__user=user)).distinct()
            