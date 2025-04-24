import re
from functools import wraps

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import re_path
from django.views.static import serve
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework.serializers import ListSerializer, ModelSerializer

from .access import Access, AdminAccess, get_field_access, GroupAccess, PrivateAccess
from .clazz import create_dynamic_class
from .string import camel_case_class_to_snake_case_string


@staff_member_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    """
    Example:
        urlpatterns = (...) + static_path(settings.MEDIA_URL, protected_serve, document_root=settings.MEDIA_ROOT)
    """
    return serve(request, path, document_root, show_indexes)


# Copied from the django.conf.urls.static(...) function.
def static_path(prefix, view=serve, **kwargs):
    return (
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs
        ),
    )


def change_permission_classes(view_set, permission_classes):
    return create_dynamic_class(view_set.__name__, view_set, {"permission_classes": permission_classes})


class ViewSetClassNameBasedNameRouter(DefaultRouter):
    def get_default_basename(self, viewset):
        tmp = camel_case_class_to_snake_case_string(viewset)
        if tmp.endswith("_view_set"):
            return tmp[:-len("_view_set")]
        raise ValueError

    def registerViewSet(self, viewset, prefix = None):
        basename = self.get_default_basename(viewset)
        return self.register(f"{prefix + '/' if prefix else ''}{basename.replace('_', '/', 1)}", viewset, basename)


class ViewSetClassNameRouter(ViewSetClassNameBasedNameRouter):
    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema

    def registerViewSet(self, viewset, prefix = None):
        assert prefix is None
        basename = self.get_default_basename(viewset)
        if basename.startswith(self.schema):
            return self.register(basename.replace(self.schema + "_", "", 1), viewset, basename)
        raise ValueError


class AccessControlRouter:
    """
    Base mixin that provides field-level access control for routers.
    """

    def _is_authenticated(self, request):
        return request.user.is_authenticated

    def _is_admin(self, request):
        return self._is_authenticated(request) and request.user.is_staff

    def _include_schema(self, request):
        return self._is_authenticated(request)

    def _filter_fields_by_access(self, serializer, request):
        serializers = [serializer]
        while len(serializers) > 0:
            s = serializers.pop()
            if isinstance(s, ListSerializer):
                s = s.child

            if isinstance(s, ModelSerializer):
                for field in s.Meta.model._meta.get_fields():
                    if field.name in s.fields:
                        access = get_field_access(field)

                        # Handle different access types.
                        if type(access) == Access:
                            continue
                        elif type(access) == PrivateAccess and self._is_authenticated(request):
                            continue
                        elif type(access) == AdminAccess and self._is_admin(request):
                            continue
                        elif (type(access) == GroupAccess and self._is_authenticated(request)
                              and request.user.groups.filter(name=access.group_name).exists()):
                            continue

                        s.fields.pop(field.name)

                serializers.extend([v for v in s.fields.values() if isinstance(v, (ModelSerializer, ListSerializer))])

        return serializer

    def _apply_access_control(self, viewset_class):
        original_get_serializer = viewset_class.get_serializer
        _include_schema = self._include_schema
        _filter_fields_by_access = self._filter_fields_by_access

        # Create new get_serializer method that filters serializers and their fields.
        @wraps(original_get_serializer)
        def new_get_serializer(self, *args, **kwargs):
            if _include_schema(self.request):
                serializer = original_get_serializer(self, *args, **kwargs)
                return _filter_fields_by_access(serializer, self.request)
            return None

        viewset_class.get_serializer = new_get_serializer

        return viewset_class


class PublicAccessControlRouter(AccessControlRouter):
    def _include_schema(self, request):
        return True

    def _apply_access_control(self, viewset_class):
        viewset_class = super()._apply_access_control(viewset_class)
        viewset_class.permission_classes = (AllowAny,)
        return viewset_class


class ViewSetClassNameBasedNameRouterAccessControlRouter(ViewSetClassNameBasedNameRouter, AccessControlRouter):
    def register(self, prefix, viewset, basename=None, **kwargs):
        """Register a viewset with access control policies applied."""
        secured_viewset = self._apply_access_control(viewset)
        super().register(prefix, secured_viewset, basename, **kwargs)


class ViewSetClassNameRouterAccessControlRouter(ViewSetClassNameRouter, AccessControlRouter):
    def registerViewSet(self, viewset, *args, **kwargs):
        """Register a viewset with access control policies applied."""
        secured_viewset = self._apply_access_control(viewset)
        super().registerViewSet(secured_viewset, *args, **kwargs)
