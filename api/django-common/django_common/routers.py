from rest_framework.routers import DefaultRouter

from django_common.utilities import (call_method_of_all_base_class_after_myself_until_not_none,
                                     camel_case_class_to_snake_case_string)


class ViewSetClassNameBasedNameRouter(DefaultRouter):
    def get_default_basename(self, viewset):
        tmp = camel_case_class_to_snake_case_string(viewset)
        if tmp.endswith("_view_set"):
            return tmp[:-len("_view_set")]
        raise ValueError


class ViewSetClassNameRouter(ViewSetClassNameBasedNameRouter):
    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema

    def registerViewSet(self, viewset):
        basename = self.get_default_basename(viewset)
        if basename.startswith(self.schema):
            prefix = basename.replace(self.schema + "_", "", 1)
            return self.register(prefix, viewset, basename)
        raise ValueError


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
