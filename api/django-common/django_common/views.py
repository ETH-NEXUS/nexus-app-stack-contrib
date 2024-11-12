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
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .authorization import IsOwnUser
from .clazz import call_method_of_all_base_class_after_myself_and_overwrite_argument
from .serializers import UserSerializer


@extend_schema(exclude=True)
class AppApiView(views.APIView):
    swagger_schema = None


class GenericAppViewSet(viewsets.GenericViewSet, AppApiView):
    pass


class BakeAllBaseFilterViewSets(mixins.ListModelMixin, viewsets.GenericViewSet):
    # TODO Does this belong here?
    permission_classes = (IsAuthenticated,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        check = False
        # TODO OpenAPI 3 (drf-spectacular)
        swagger_auto_schema = {"manual_parameters": []}
        for c in self.__class__.__bases__:
            if c == BakeAllBaseFilterViewSets:
                check = True
            if check:
                tmp = getattr(getattr(super(c, self), "list", {}), '_swagger_auto_schema', {})
                if "manual_parameters" in tmp:
                    swagger_auto_schema["manual_parameters"] = (swagger_auto_schema["manual_parameters"]
                                                                + tmp["manual_parameters"])

        self._original_list = self.list

        def new_list(request, *_args, **_kwargs):
            return self._original_list(request, *_args, **_kwargs)

        self.list = new_list
        self.list._swagger_auto_schema = swagger_auto_schema

    def filter_queryset(self, queryset):
        return call_method_of_all_base_class_after_myself_and_overwrite_argument(
            BakeAllBaseFilterViewSets,
            self,
            "filter_queryset",
            queryset
        )


class VersionView(AppApiView):
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


class UserViewSet(GenericAppViewSet):
    permission_classes = (IsOwnUser,)
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=("get",))
    def me(self, request):
        user = self.get_queryset().get(id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
