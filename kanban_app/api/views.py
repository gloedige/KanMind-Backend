
from django.db.models import Q
from rest_framework import generics, serializers, viewsets
from .permissions import IsOwnerOrMember, IsMemberOfBoard
from rest_framework.permissions import IsAuthenticated
from ..models import Board, Task
from .serializers import BoardListSerializer, BoardDetailSerializer, TaskDetailSerializer, TaskListSerializer

class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing boards.
    Provides CRUD operations for boards.
    Permissions:
        - IsAuthenticated: User must be authenticated.
        - IsOwnerOrMember: User must be the owner or a member of the board.
    Methods:
        - perform_create(self, serializer): Sets the owner of the board to the current user upon creation.
        - get_queryset(self): Returns the queryset of boards the user owns or is a member of.
        - get_serializer_class(self): Returns the appropriate serializer class based on the action.
    """
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer
    permission_classes = [IsOwnerOrMember]
    
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
    """
    ViewSet for managing tasks.
    Provides CRUD operations for tasks.
    Permissions:
        - IsMemberOfBoard: User must be a member of the board to perform actions on tasks.
    Methods:
        - perform_create(self, serializer): Sets the assignee and reviewer of the task upon creation.
        - get_queryset(self): Returns the queryset of tasks for the specified board and user.
        - get_serializer_class(self): Returns the appropriate serializer class based on the action.
    """
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsMemberOfBoard]

    def perform_create(self, serializer):
        assignee_id = self.request.data.get('assignee_id', None)
        reviewer_id = self.request.data.get('reviewer_id', None)
        serializer.save(assignee_id=assignee_id, reviewer_id=reviewer_id)

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(board__owner=user) | Q(board__members__user=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action in ['update', 'destroy', 'partial_update']:
            return TaskDetailSerializer
        return TaskListSerializer
            