from functools import wraps

from rest_framework.permissions import AllowAny

from .access import get_field_access, Private, Admin, Group
from .clazz import call_method_of_all_base_class_after_myself_until_not_none
from .urls import ViewSetClassNameBasedNameRouter, ViewSetClassNameRouter
from rest_framework import serializers

class AppLabelConnectionRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model._meta, "app_label_routing"):
            if model._meta.app_label_routing == True:
                return model._meta.app_label
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model._meta, "app_label_routing"):
            if model._meta.app_label_routing == True:
                return model._meta.app_label
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == app_label:
            return True
        return None


class DefaultConnectionRouter:
    def db_for_read(self, model, **hints):
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return True
        return False


class CakeConnectionRouter:
    def db_for_read(self, model, **hints):
        return call_method_of_all_base_class_after_myself_until_not_none(
            CakeConnectionRouter,
            self,
            "db_for_read",
            model,
            **hints
        )

    def db_for_write(self, model, **hints):
        return call_method_of_all_base_class_after_myself_until_not_none(
            CakeConnectionRouter,
            self,
            "db_for_write",
            model,
            **hints
        )

    def allow_relation(self, obj1, obj2, **hints):
        return call_method_of_all_base_class_after_myself_until_not_none(
            CakeConnectionRouter,
            self,
            "allow_relation",
            obj1,
            obj2,
            **hints
        )

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return call_method_of_all_base_class_after_myself_until_not_none(
            CakeConnectionRouter,
            self,
            "allow_migrate",
            db,
            app_label,
            model_name,
            **hints
        )


class AccessControlRouterBase:
    """
    Base mixin that provides field-level access control for routers.
    """

    def __init__(self, is_public=False, **kwargs):
        self.is_public = is_public
        super().__init__(**kwargs)

    def _filter_fields_by_access(self, serializer, request):
        is_admin = request.user.is_authenticated and request.user.is_staff
        is_authenticated = request.user.is_authenticated

        if isinstance(serializer, serializers.ListSerializer):
            target = serializer.child
        else:
            target = serializer

        model_class = None
        if hasattr(target, 'Meta') and hasattr(target.Meta, 'model'):
            model_class = target.Meta.model
        else:
            return serializer

        fields_to_remove = []

        model_fields = {}
        for field in model_class._meta.get_fields():
            if hasattr(field, 'name'):
                model_fields[field.name] = get_field_access(field)

        for field_name, field in target.fields.items():
            if field_name not in model_fields:
                continue

            access = model_fields[field_name]

            # Handle different access types
            if isinstance(access, Private) and not is_authenticated:
                fields_to_remove.append(field_name)
            elif isinstance(access, Admin) and (not is_authenticated or not is_admin):
                fields_to_remove.append(field_name)
            elif isinstance(access, Group) and (not is_authenticated or
                                                not request.user.groups.filter(name=access.group_name).exists()):
                fields_to_remove.append(field_name)

        for field_name in fields_to_remove:
            target.fields.pop(field_name, None)

        return serializer

    def _apply_access_control(self, viewset_class):
        if self.is_public:
            viewset_class.permission_classes = (AllowAny,)

        original_get_serializer = viewset_class.get_serializer

        # Create new get_serializer method that filters fields
        @wraps(original_get_serializer)
        def new_get_serializer(self, *args, **kwargs):
            serializer = original_get_serializer(self, *args, **kwargs)
            return self.router._filter_fields_by_access(serializer, self.request)

        viewset_class.get_serializer = new_get_serializer
        viewset_class.router = self

        return viewset_class

    def register(self, prefix, viewset, basename=None, **kwargs):
        """Register a viewset with access control policies applied."""
        secured_viewset = self._apply_access_control(viewset)
        super().register(prefix, secured_viewset, basename, **kwargs)

    def registerViewSet(self, viewset_class, *args, **kwargs):
        """Register a viewset with access control policies applied."""
        secured_viewset = self._apply_access_control(viewset_class)
        super().registerViewSet(secured_viewset, *args, **kwargs)


class AccessControlRouter(AccessControlRouterBase, ViewSetClassNameBasedNameRouter):
    pass


class SchemaAccessControlRouter(AccessControlRouterBase, ViewSetClassNameRouter):
    pass


def PublicRouter(schema=None, **kwargs):
    kwargs['is_public'] = True
    if schema is not None:
        return SchemaAccessControlRouter(schema=schema, **kwargs)
    return AccessControlRouter(**kwargs)


def PrivateRouter(schema=None, **kwargs):
    kwargs['is_public'] = False
    if schema is not None:
        return SchemaAccessControlRouter(schema=schema, **kwargs)
    return AccessControlRouter(**kwargs)
