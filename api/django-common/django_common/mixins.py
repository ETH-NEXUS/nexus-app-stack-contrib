from rest_framework import viewsets, permissions, mixins


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
