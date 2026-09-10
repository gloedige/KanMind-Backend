from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

class IsOwnerOrMemer(BasePermission):
    def has_object_permission(self, request, view, board):

        if request.method in SAFE_METHODS:
            return True
        if board.owner == request.user:
            return True
        if request.user in board.members.all():
            return True
        #TODO hier dürfen nur Mitglieder Änderungen vornehmen, nicht alle member
        return board.members.filter(id=request.user.id).exists()

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated