from rest_framework import permissions


class IsOwnUser(permissions.BasePermission):
    """
    Object-level permission to only allow to get the user object of himself.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id


class OwnedModelMixin:
    """
    The OwnedModelMixin needs to be mixed into ModelViewSet
    with referencing a OwnedModel.
    """

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        return [permission() for permission in self.permission_classes] + [
            permissions.IsAuthenticated()
        ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
