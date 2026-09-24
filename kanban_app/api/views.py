
import email
from rest_framework import routers, viewsets
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import generics, serializers, viewsets
from .permissions import IsOwnerOfTaskOrBoardForDestroy, IsOwnerOrMember, IsMemberOfBoard, IsOwnerForDestroy
from rest_framework.permissions import IsAuthenticated, Http404
from rest_framework.exceptions import ValidationError
from ..models import Board, Task, User
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardUpdateSerializer, TaskDetailSerializer, TaskListSerializer, EmailListSerializer

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
    permission_classes = [IsOwnerOrMember, IsOwnerForDestroy]
    
    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(members__user=user)).distinct()
    
    def get_serializer_class(self):
        if self.action in ['retrieve', 'destroy']:
            return BoardDetailSerializer
        if self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
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
        - check_is_member_of_board(self): Checks if the assignee and reviewer are members of the board and raises a ValidationError if not.
    """
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer
    permission_classes = [IsMemberOfBoard, IsOwnerOfTaskOrBoardForDestroy]

    def initial(self, request, *args, **kwargs):
        if self.action in ['destroy', 'partial_update']:
            task_id = self.kwargs.get('pk', None)
            if not self.checkTaskIdIsValid(task_id):
                raise ValidationError({"error": "Invalid task ID."})
            if not self.checkTaskIdExists(task_id):
                raise Http404({"error": "Task ID does not exist."})
        super().initial(request, *args, **kwargs)

    def perform_create(self, serializer):
        assignee_id = self.request.data.get('assignee_id', None)
        reviewer_id = self.request.data.get('reviewer_id', None)
        task_owner_id = self.request.user.id
        serializer.save(assignee_id=assignee_id, reviewer_id=reviewer_id, owner_id=task_owner_id)

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(Q(board__owner=user) | Q(board__members__user=user)).distinct()

    def get_serializer_class(self):
        if self.action in ['destroy', 'partial_update']:
            return TaskDetailSerializer
        return TaskListSerializer

    def checkTaskIdIsValid(self, task_id):
        task_id_not_none = task_id is not None
        task_id_is_digit = str(task_id).isdigit()
        return task_id_not_none and task_id_is_digit

    def checkTaskIdExists(self, task_id):
        return Task.objects.filter(pk=task_id).exists()
    

class EmailViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing emails.
    Provides CRUD operations for emails.
    Permissions:
        - IsAuthenticated: User must be authenticated.
    Methods:
        - get_queryset(self): Returns the queryset of users filtered by the validated email address.
        - validate_email_address(self, emailToCheck): Validates the provided email address and raises a ValidationError if it is invalid.
    """
    queryset = User.objects.all()
    serializer_class = EmailListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        email = self.request.query_params.get('email', None)
        validated_email = None
        filtered_email = None
        if email:
            validated_email = self.validate_email_address(email)
        
        filtered_email = User.objects.filter(email=validated_email)
        if not filtered_email.exists():
            raise Http404("Email not found.")
        return filtered_email

    def validate_email_address(self, emailToCheck):
        if emailToCheck is None or emailToCheck.strip() == '':
            raise serializers.ValidationError("Email is required.")
        try:
            validate_email(emailToCheck)
        except Exception:
            raise serializers.ValidationError("Invalid email address.")
        return emailToCheck
            