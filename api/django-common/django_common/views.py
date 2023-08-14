import json
from os import environ

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from rest_framework import status, viewsets
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsOwnUser
from .serializers import UserSerializer


class VersionView(views.APIView):
    @staticmethod
    def get(request):
        return Response({"version": environ.get("GIT_VERSION") or "𝛼"})


class CsrfCookieView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request: WSGIRequest, *args, **kwargs):
        return JsonResponse({"details": _("CSRF cookie set")})


class LoginView(View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if username is None or password is None:
            return JsonResponse(
                {"detail": _("Please provide username and password.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(username=username, password=password)

        if user is None:
            return JsonResponse(
                {"detail": _("Invalid credentials.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        login(request, user)
        return JsonResponse({"detail": _("Successfully logged in.")})


class LogoutView(View):
    def get(self, request: WSGIRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {"detail": _("You're not logged in.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logout(request)
        return JsonResponse({"detail": _("Successfully logged out.")})


class UserViewSet(viewsets.GenericViewSet):
    permission_classes = (IsOwnUser,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=("get",))
    def me(self, request):
        user = self.get_queryset().get(id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
