from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.db.models import Q
from django.http import Http404
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from kanban_app.utils import checkCommentIdExists, checkTaskIdExists, checkIdIsValid, checkBoardIdExists

from ..models import Board, Comment, Member, Task
from .permissions import IsMemberOfBoard, IsOwnerOfBoardForDestroy, IsOwnerOfTaskOrBoardForDestroy, IsOwnerOrMember, IsOwnerOfCommentForDestroy
from .serializers import BoardDetailSerializer, BoardListSerializer, BoardUpdateSerializer, CommentListSerializer, MemberSerializer, TaskDetailSerializer, TaskListSerializer

User = get_user_model()

class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing boards.
    Provides CRUD operations for boards.
    Permissions:
        - IsAuthenticated: User must be authenticated.
        - IsOwnerOrMember: User must be the owner or a member of the board.
        
    """
    queryset = Board.objects.all()
    serializer_class = BoardListSerializer

    def initial(self, request, *args, **kwargs):
            """
            Validates the board ID before processing the request.
            Raises a ValidationError if the ID is invalid.
            Raises an Http404 if the board does not exist.
            """
            self._validate_board_id()
            super().initial(request, *args, **kwargs)
    
    def get_permissions(self):
            """
            Returns the list of permission classes for the current action.
            """
            if self.action == 'destroy':
                permission_classes = [IsAuthenticated, IsOwnerOfBoardForDestroy]
            else:
                permission_classes = [IsAuthenticated, IsOwnerOrMember]
            return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Returns the queryset of boards for the current user.
        The user must be either the owner or a member of the board.
        """
        user = self.request.user
        return Board.objects.filter(Q(owner=user) | Q(board_members__user=user)).distinct()
    
    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the current action.
        """
        if self.action in ['retrieve', 'destroy']:
            return BoardDetailSerializer
        if self.action in ['update', 'partial_update']:
            return BoardUpdateSerializer
        return BoardListSerializer

    def _validate_board_id(self):
        """
        Validates the board ID for actions that require it.
        Raises a ValidationError if the ID is invalid.
        Raises an Http404 if the board does not exist.
        """
        if self.action not in ['retrieve', 'destroy', 'update', 'partial_update']:
            return
        board_id = self.kwargs.get('pk', None)
        if not checkIdIsValid(board_id):
            raise ValidationError({"error": "Invalid board ID."})
        if not checkBoardIdExists(board_id):
                raise Http404({"error": "Board ID does not exist."})
    

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.
    Provides CRUD operations for tasks.
    Permissions:
        - IsMemberOfBoard: User must be a member of the board to perform actions on tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer

    def initial(self, request, *args, **kwargs):
        """
        Validates the task ID for actions that require it.
        Raises a ValidationError if the ID is invalid.
        Raises an Http404 if the task does not exist.
        """
        if self.action in ['destroy', 'partial_update']:
            task_id = self.kwargs.get('pk', None)
            if not checkIdIsValid(task_id):
                raise ValidationError({"error": "Invalid task ID."})
            if not checkTaskIdExists(task_id):
                raise Http404({"error": "Task ID does not exist."})
        super().initial(request, *args, **kwargs)

    def get_permissions(self):
            """
            Returns the list of permission classes for the current action.
            """
            if self.action == 'destroy':
                permission_classes = [IsAuthenticated, IsOwnerOfTaskOrBoardForDestroy]
            else:
                permission_classes = [IsAuthenticated, IsMemberOfBoard]
            return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """
        Sets the assignee, reviewer, and owner of the task upon creation.
        """
        assignee_id = self.request.data.get('assignee_id', None)
        reviewer_id = self.request.data.get('reviewer_id', None)
        task_owner_id = self.request.user.id
        serializer.save(assignee_id=assignee_id, reviewer_id=reviewer_id, owner_id=task_owner_id)

    def get_queryset(self):
        """
        Returns the queryset of tasks for the current user, including tasks from boards they own or are a member of.
        """
        user = self.request.user
        return Task.objects.filter(Q(board__owner=user) | Q(board__members=user)).distinct()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the current action.
        Uses TaskDetailSerializer for 'destroy' and 'partial_update' actions, and TaskListSerializer for other actions.
        """
        if self.action in ['destroy', 'partial_update']:
            return TaskDetailSerializer
        return TaskListSerializer

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request, *args, **kwargs):
        """
        Returns the list of tasks assigned to the current user.
        """
        member = Member.objects.filter(user_id=request.user.id).first()
        if member:
            tasks = Task.objects.filter(Q(assignee_id=member.user_id)).distinct()
            return Response(TaskListSerializer(tasks, many=True).data)
        return Response(TaskListSerializer([], many=True).data)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request, *args, **kwargs):
        """
        Returns the list of tasks the current user is reviewing.
        """
        member = Member.objects.filter(user_id=request.user.id).first()
        if member:
            tasks = Task.objects.filter(Q(reviewer_id=member.user_id)).distinct()

            return Response(TaskListSerializer(tasks, many=True).data)
        return Response(TaskListSerializer([], many=True).data)
    

class EmailDetailView(APIView):
    """
    ViewSet for managing emails.
    Provides CRUD operations for emails.
    Permissions:
        - IsAuthenticated: User must be authenticated.
    """
    queryset = User.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieves the user associated with the provided email address.
        """
        email = self.request.query_params.get('email', None)
        validated_email = None
        user_by_email = None
        if email:
            validated_email = self.validate_email_address(email).lower()
        try:
            user_by_email = User.objects.get(email=validated_email)
            return Response(MemberSerializer(user_by_email, many=False).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'detail': 'User with this email not found'}, status=status.HTTP_404_NOT_FOUND)

    def validate_email_address(self, emailToCheck):
        """
        Validates the provided email address and raises a ValidationError if it is invalid.
        Returns the validated email address.
        """
        if emailToCheck is None or emailToCheck.strip() == '':
            raise serializers.ValidationError("Email is required.")
        try:
            validate_email(emailToCheck)
        except Exception:
            raise serializers.ValidationError("Invalid email address.")
        return emailToCheck

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing comments.
    Provides CRUD operations for comments associated with tasks.
    Permissions:
        - IsMemberOfBoard: User must be a member of the board associated with the task.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer

    def get_permissions(self):
        """
        Returns the appropriate permission classes based on the current action.
        Uses IsOwnerOfCommentForDestroy for the 'destroy' action, and IsMemberOfBoard for other actions.
        """
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsOwnerOfCommentForDestroy]
        else:
            permission_classes = [IsAuthenticated, IsMemberOfBoard]
        return [permission() for permission in permission_classes]

    def initial(self, request, *args, **kwargs):
        """
        Validates the task and comment context before processing the request.
        Raises ValidationError or Http404 if the context is invalid.
        """
        self._validate_task_context()
        self._validate_comment_context_for_destroy()
        super().initial(request, *args, **kwargs)

    def _validate_task_context(self):
        """
        Validates the task context by checking if the task ID is valid and exists.
        Raises ValidationError or Http404 if the task context is invalid.
        """
        task_id = self.kwargs.get('task_pk', None)
        if not checkIdIsValid(task_id):
            raise ValidationError({"error": "Invalid task ID."})
        if not checkTaskIdExists(task_id):
            raise Http404({"error": "Task ID does not exist."})

    def _validate_comment_context_for_destroy(self):
        """
        Validates the comment context for the destroy action by checking if the comment ID is valid and exists.
        Raises ValidationError or Http404 if the comment context is invalid.
        """
        if self.action != 'destroy':
            return
        comment_id = self.kwargs.get('pk', None)
        if not checkIdIsValid(comment_id):
            raise ValidationError({"error": "Invalid comment ID."})
        if not checkCommentIdExists(comment_id):
            raise Http404({"error": "Comment ID does not exist."})

    def get_queryset(self):
        """
        Returns the queryset of comments filtered by the task ID if provided.
        """
        task_id = self.kwargs.get('task_pk', None)
        if task_id:
            return Comment.objects.filter(task_id=task_id)
        return Comment.objects.all()

    def perform_create(self, serializer):
        """
        Performs the creation of a new comment, associating it with the current user and the specified task.
        """
        author_name = self.request.user.username
        task_id = self.kwargs.get('task_pk', None)
        serializer.save(author=author_name, task_id=task_id)
            