from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from django.http import Http404
from rest_framework.permissions import SAFE_METHODS
from kanban_app.models import Board, Task, Comment

"""
This module contains custom permission classes and helper functions for the Kanban app.
"""

def check_board_existence_by_board_id(board_id):
    """
    Checks if a board with the given board_id exists.
    Raises Http404 if the board does not exist.
    Returns the board instance if it exists.
    """
    try:
        board = Board.objects.get(pk=board_id)
    except Board.DoesNotExist:
        raise Http404("Board not found!")
    return board

def check_board_existence_by_task_id(task_id):
    """
    Checks if a task with the given task_id exists and retrieves its associated board.
    Raises Http404 if the task does not exist.
    Returns the board instance if the task exists.
    """
    try:
        board = Task.objects.select_related('board').get(pk=task_id).board
    except Task.DoesNotExist:
        raise Http404("Task not found!")
    return board

def check_comment_existence_by_comment_id(comment_id):
    """
    Checks if a comment with the given comment_id exists.
    Raises Http404 if the comment does not exist.
    Returns the comment instance if it exists.
    """
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        raise Http404("Comment not found!")
    return comment

def check_task_existence_by_task_id(task_id):
    """
    Checks if a task with the given task_id exists.
    Raises Http404 if the task does not exist.
    Returns the task instance if it exists.
    """
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise Http404("Task not found!")
    return task


class IsOwnerOrMember(BasePermission):
    """
    Permission class to check if the user is the owner or a member of the board.
    """
    def has_permission(self, request, view):
        """
        Checks if the user has permission to access the board based on ownership or membership.
        Returns True if the user is the owner or a member of the board, False otherwise.
        Raises PermissionDenied if the user is not the owner or a member.
        """
        board_id = view.kwargs.get('pk')
        if board_id is None:
            return True
        
        board = check_board_existence_by_board_id(board_id)
        return self.is_user_owner_or_member(board, request)

    def is_user_owner_or_member(self, board, request):
        """
        Checks if the user is the owner or a member of the given board.
        Raises PermissionDenied if the user is not the owner or a member.
        Returns True if the user is the owner or a member, False otherwise.
        """
        is_owner_or_member = board.owner_id == request.user.id or board.board_members.filter(user_id=request.user.id).exists()
        if not is_owner_or_member:
            raise PermissionDenied("You are not the owner or a member of this board.")
        return is_owner_or_member
        

class IsMemberOfBoard(BasePermission):
    """
    Permission class to check if the user is a member of the board.
    """
    def has_permission(self, request, view):     
        """
        Checks if the user has permission to access the board based on membership.
        Returns True if the user is a member of the board, False otherwise.
        Raises PermissionDenied if the user is not a member.
        """
        board = self.get_board_from_view(request, view)
        if board is None:
            return True
        return self.is_user_member(board, request)

    def get_board_from_view(self, request, view):
        """
        Retrieves the board instance based on the request data and view context.
        Returns the board instance if found, None otherwise.
        """
        board_id = request.data.get('board')
        if board_id is not None:
            return check_board_existence_by_board_id(board_id)
    
        if 'task_pk' in view.kwargs and view.kwargs['task_pk'] is not None:
            task_id = view.kwargs['task_pk']
        elif 'pk' in view.kwargs and view.kwargs['pk'] is not None:
            task_id = view.kwargs['pk']
        else:
            return None
    
        return check_board_existence_by_task_id(task_id)

    def is_user_member(self, board, request):
        """
        Checks if the user is a member of the given board.
        Raises PermissionDenied if the user is not a member.
        Returns True if the user is a member, False otherwise.
        """
        is_member = board.board_members.filter(user_id=request.user.id).exists()
        if not is_member:
            raise PermissionDenied("You are not a member of this board.")
        return is_member

class IsOwnerOfBoardForDestroy(BasePermission):
    """
    Permission class to check if the user is the owner of the board for destroy action.
    """

    def has_permission(self, request, view):
        """
        Checks if the user has permission to access the board for the destroy action.
        Returns True if the user is the owner of the board, False otherwise.
        Raises PermissionDenied if the user is not the owner.
        """
        board_id = view.kwargs.get('pk')
        if board_id is None:
            return True
        
        board = check_board_existence_by_board_id(board_id)
        return self.is_user_owner(board, request)

    def is_user_owner(self, board, request):
        """
        Checks if the user is the owner of the given board.
        Raises PermissionDenied if the user is not the owner.
        Returns True if the user is the owner, False otherwise.
        """
        is_owner = board.owner_id == request.user.id
        if not is_owner:
            raise PermissionDenied("You are not the owner of this board.")
        return is_owner

class IsOwnerOfCommentForDestroy(BasePermission):
    """
    Permission class to check if the user is the owner of the comment for destroy action.
    """

    def has_permission(self, request, view):
        """
        Checks if the user has permission to access the comment for the destroy action.
        Returns True if the user is the owner of the comment, False otherwise.
        Raises PermissionDenied if the user is not the owner.
        """
        comment_id = view.kwargs.get('pk')
        if comment_id is None:
            return True
        
        comment = check_comment_existence_by_comment_id(comment_id)
        return self.is_user_comment_owner(comment, request)

    def is_user_comment_owner(self, comment, request):
        """
        Checks if the user is the owner of the given comment.
        Raises PermissionDenied if the user is not the owner.
        Returns True if the user is the owner, False otherwise.
        """
        is_owner = comment.author == request.user.username
        if not is_owner:
            raise PermissionDenied("You are not the owner of this comment.")
        return is_owner
     

class IsOwnerOfTaskOrBoardForDestroy(BasePermission):
    """
    Permission class to check if the user is the owner of the task or its board for the destroy action.
    """
    def has_permission(self, request, view):
        """
        Checks if the user has permission to access the task for the destroy action.
        Returns True if the user is the owner of the task or its board, False otherwise.
        Raises PermissionDenied if the user is not the owner.
        """
        task_id = view.kwargs.get('pk')
        if task_id is None:
            return True
        
        task = check_task_existence_by_task_id(task_id)
        return self.is_user_task_or_board_owner(task, request)

    def is_user_task_or_board_owner(self, task, request):
        """
        Checks if the user is the owner of the given task or its board.
        Raises PermissionDenied if the user is not the owner.
        Returns True if the user is the owner, False otherwise.
        """
        is_owner = task.owner_id == request.user.id or task.board.owner_id == request.user.id
        if not is_owner:
            raise PermissionDenied("You are not the owner of this task or its board.")
        return is_owner