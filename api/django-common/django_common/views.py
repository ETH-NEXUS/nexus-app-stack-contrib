import json
from os import environ
from types import MappingProxyType

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

from .access import _get_field_access, _is_authentication_required
from .authorization import IsOwnUser
from .serializers import UserSerializer
from .spectacular import _AUTH_EXTENSION


@extend_schema(exclude=True)
class AppApiView(views.APIView):
    pass


class AppGenericViewSet(viewsets.GenericViewSet, AppApiView):
    pass


class StaticFilterQuerysetViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    def __init__(self, data={}, **kwargs):
        super().__init__(**kwargs)
        # Makes "data" immutable.
        self.data = MappingProxyType(data)

    @staticmethod
    def static_filter_queryset(query_params, data, queryset):
        pass


def _bake_all_base_filter_view_sets(cls):
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

    def x_access(parameters, model_fields):
        if not len(parameters) > 1:
            for parameter in parameters:
                if parameter.extensions and _AUTH_EXTENSION in parameter.extensions:
                    return True
        for model_field in model_fields:
            for parameter in parameters:
                if model_field.name == parameter.name:
                    access = _get_field_access(model_field)
                    if _is_authentication_required(access):
                        if parameter.extensions:
                            parameter.extensions[_AUTH_EXTENSION] = str(access)
                        else:
                            parameter.extensions = {_AUTH_EXTENSION: str(access)}
                        return True
        return False

    def get_filter_queryset(cls):
        return cls.filter_queryset if "filter_queryset" in cls.__dict__ else None

    def get_static_filter_queryset(cls):
        return cls.static_filter_queryset if "static_filter_queryset" in cls.__dict__ else None

    anonymous_static_filter_querysets = []
    authenticated_static_filter_querysets = []
    filter_queryset = None
    parameters = []

    model_fields = cls.serializer_class.Meta.model._meta.get_fields()

    for c in [cls] + list(cls.__bases__):
        if c not in (mixins.ListModelMixin, viewsets.GenericViewSet):
            tmp_parameters = get_override_parameters(c)
            if tmp_parameters:
                if static_filter_queryset := get_static_filter_queryset(c):
                    if x_access(tmp_parameters, model_fields):
                        authenticated_static_filter_querysets.append(static_filter_queryset)
                    else:
                        anonymous_static_filter_querysets.append(static_filter_queryset)
                if tmp_filter_queryset := get_filter_queryset(c):
                    filter_queryset = tmp_filter_queryset
                if static_filter_queryset or tmp_filter_queryset:
                    parameters.extend(tmp_parameters)
                    continue
                if c == cls:
                    continue

                raise AssertionError(f"Due to the OpenAPI parameters ({[p.name for p in tmp_parameters]}) of the {c} "
                                     "class, the class must implement at least one type of a filter QuerySet method.")

    if parameters:
        def new_filter_queryset(self, queryset):
            if authenticated_static_filter_querysets and self.request.user.is_authenticated:
                for f in authenticated_static_filter_querysets:
                    queryset = f(self.request.query_params, self.data, queryset)
            for f in anonymous_static_filter_querysets:
                queryset = f(self.request.query_params, self.data, queryset)
            if filter_queryset:
                queryset = filter_queryset(self, queryset)
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


class UserViewSet(AppGenericViewSet):
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
