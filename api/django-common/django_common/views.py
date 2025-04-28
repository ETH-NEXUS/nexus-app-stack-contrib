import json
from os import environ

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework import views
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from .authorization import IsOwnUser
from .serializers import UserSerializer


@extend_schema(exclude=True)
class AppApiView(views.APIView):
    pass


class GenericAppViewSet(viewsets.GenericViewSet, AppApiView):
    pass


def bake_all_base_filter_view_sets(cls):
    dummy_api_view = APIView()
    dummy_api_view.request = APIRequestFactory().post(None)
    dummy_api_view.kwargs = {}

    def get_override_parameters(c):
        kwargs = getattr(getattr(c, "list", None), "kwargs", {})
        if "schema" in kwargs:
            o = kwargs["schema"]()
            o.view = dummy_api_view
            return o.get_override_parameters()
        return []

    parameters = get_override_parameters(cls)
    for b in cls.__bases__:
        parameters.extend(get_override_parameters(b))

    if len(parameters) > 0:
        filter_queryset = cls.filter_queryset if "filter_queryset" in cls.__dict__ else None
        valid_view_set_base_classes = tuple(b for b in cls.__bases__ if b not in (mixins.ListModelMixin, viewsets.GenericViewSet))

        def new_filter_queryset(self, queryset):
            if filter_queryset:
                queryset = filter_queryset(self, queryset)
            for valid_view_set_base_class in valid_view_set_base_classes:
                queryset = getattr(valid_view_set_base_class, "filter_queryset")(self, queryset)
            return queryset

        cls.filter_queryset = new_filter_queryset
        return extend_schema_view(list=extend_schema(parameters=parameters))(cls)

    return cls


class VersionView(AppApiView):
    @staticmethod
    def get(request):
        return Response({"version": settings.SPECTACULAR_SETTINGS["VERSION"]
            if hasattr(settings, "SPECTACULAR_SETTINGS") and "VERSION" in settings.SPECTACULAR_SETTINGS
                else environ.get("GIT_VERSION") or "𝛼"})


class CsrfCookieView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request: WSGIRequest, *args, **kwargs):
        return JsonResponse({"details": _("CSRF cookie set")})


class LoginView(View):
    def post(self, request: WSGIRequest, *args, **kwargs):
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
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

        if not request.user.is_authenticated:
            return Response(
                {"detail": "User not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = self.get_queryset().get(id=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)
