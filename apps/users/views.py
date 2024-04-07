from rest_access_policy import AccessViewSetMixin
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.users.models import User
from apps.users.permissions import UserAccessPolicy
from apps.users.serializers import UserSerializer


class UserViewSet(AccessViewSetMixin, ModelViewSet):
    """ViewSet for the User class."""

    queryset = User.objects.all()
    lookup_field = "uuid"
    serializer_class = UserSerializer
    access_policy = UserAccessPolicy

    @action(detail=False, methods=["GET"])
    def me(self, request: Request):
        """Return the current user."""
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)
