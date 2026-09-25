from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http import Http404
from rest_framework.permissions import SAFE_METHODS
from kanban_app.models import Board, Task

"""
This module contains custom permission classes and helper functions for the Kanban app.
Methods
-------
check_board_existence_by_board_id(board_id)
check_board_existence_by_task_id(task_id)
"""

def check_board_existence_by_board_id(board_id):
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise Http404("Board not found!")
        return board

def check_board_existence_by_task_id(task_id):
    try:
        board = Task.objects.select_related('board').get(pk=task_id).board
    except Task.DoesNotExist:
        raise Http404("Task not found!")
    return board

class IsOwnerOrMember(BasePermission):
    """
    Permission class to check if the user is the owner or a member of the board.
    Methods
    -------
    has_permission(self, request, view)
        Checks if the user has permission to access the board based on ownership or membership.
    is_user_owner_or_member(board, request)
        Checks if the user is the owner or a member of the given board.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("You must be authenticated to perform this action.")

        board_id = view.kwargs.get('pk')
        if board_id is None:
            return True
        
        board = check_board_existence_by_board_id(board_id)
        return IsOwnerOrMember.is_user_owner_or_member(board, request)

    def is_user_owner_or_member(board, request):
        is_owner_or_member = board.owner_id == request.user.id or board.members.filter(user_id=request.user.id).exists()
        if not is_owner_or_member:
            raise PermissionDenied("You are not the owner or a member of this board.")
        return is_owner_or_member
        

class IsMemberOfBoard(BasePermission):
    """
    Permission class to check if the user is a member of the board.
    Methods
    -------
    has_permission(self, request, view)
        Checks if the user has permission to access the board based on membership.
    check_board_existence(board_id)
        Checks if the board with the given ID exists and returns it.
    is_user_member(board, request)
        Checks if the user is a member of the given board.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("You must be authenticated to perform this action.")
        
        board = self.get_board_from_view(request, view)
        if board is None:
            return True
        return self.is_user_member(board, request)

    def get_board_from_view(self, request, view):
        board_id = request.data.get('board')
        if board_id is not None:
            return check_board_existence_by_board_id(board_id)

        task_id = view.kwargs.get('pk') 
        if task_id is None:
            task_id = view.kwargs.get('task_pk')
        if task_id is None:
            return None

        return check_board_existence_by_task_id(task_id)

    def is_user_member(self, board, request):
        is_member = board.members.filter(user_id=request.user.id).exists()
        if not is_member:
            raise PermissionDenied("You are not a member of this board.")
        return is_member

class IsOwnerForDestroy(BasePermission):
     """
     Permission class to check if the user is the owner of the board for destroy action.
     Methods
     -------
     has_permission(self, request, view)
         Checks if the user has permission to destroy the board based on ownership.
     is_user_owner(board, request)
         Checks if the user is the owner of the given board.
     -------
     has_object_permission(self, request, view, obj)
         Checks if the user has permission to delete the board based on ownership.
     """
     def has_object_permission(self, request, view, obj):
        if view.action == 'destroy':
            if obj.owner_id != request.user.id:
                raise PermissionDenied("You are not the owner of this board.")
            return obj.owner_id == request.user.id

        return True

class IsOwnerOfTaskOrBoardForDestroy(BasePermission):
    """
    Permission class to check if the user is the owner of the task or board for destroy action.
    Methods
    -------
    has_object_permission(self, request, view, obj)
        Checks if the user has permission to delete the task or board based on ownership.
    """
    def has_object_permission(self, request, view, obj):
        if view.action == 'destroy':
            if hasattr(obj, 'owner_id') and obj.owner_id != request.user.id:
                raise PermissionDenied("You are not the owner of this object.")
            return hasattr(obj, 'owner_id') and obj.owner_id == request.user.id

        return True