from rest_framework.permissions import BasePermission
from rest_framework.permissions import SAFE_METHODS

class IsOwnerOrMember(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, board):
        is_owner = board.owner.id == request.user.id
        is_member = board.members.filter(id=request.user.id).exists()

        return is_owner or is_member
