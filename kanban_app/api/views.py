
from django.db.models import Q
from rest_framework import generics, serializers, viewsets
from .permissions import IsOwnerOrMember, IsMemberOfBoard
from rest_framework.permissions import IsAuthenticated
from ..models import Board, Task
from .serializers import BoardListSerializer, BoardDetailSerializer, TaskDetailSerializer, TaskListSerializer

class BoardViewSet(viewsets.ModelViewSet):
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

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsMemberOfBoard]

    def perform_create(self, serializer):
        assignee_id = self.request.data.get('assignee_id', None)
        reviewer_id = self.request.data.get('reviewer_id', None)
        serializer.save(assignee_id=assignee_id, reviewer_id=reviewer_id)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        board = Board.objects.get(pk=pk)
        user = self.request.user
        return Task.objects.filter(Q(board=board) | Q(board__members__user=user)).distinct()

    def get_serializer_class(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return TaskDetailSerializer
        return TaskListSerializer
            