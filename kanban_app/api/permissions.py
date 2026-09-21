from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed
from django.http import Http404
from rest_framework.permissions import SAFE_METHODS
from kanban_app.models import Board

class IsOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        board_id = view.kwargs.get('pk')
        if not board_id:
            return True
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return True   # dann kommt 404

        return (
            board.owner_id == request.user.id
            or board.members.filter(id=request.user.id).exists()
        )

class IsMemberOfBoard(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication credentials were not provided.")
        board_id = request.data.get('board')
        if board_id is None:
            return True
        
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise Http404("Board not found!")
        
        return board.members.filter(user_id=request.user.id).exists()
