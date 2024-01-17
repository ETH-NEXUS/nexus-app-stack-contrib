from django.db.models import Model
from collections import OrderedDict
from .query import TableFunctionManager


class UdfConnectionRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model, "using"):
            return model.using
        return None

    def db_for_write(self, model, **hints):
        if hasattr(model, "using"):
            return model.using
        return None

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "udf":
            return False
        return None


class UdfModel(Model):
    using = "udf"
    function_args = OrderedDict()
    objects = TableFunctionManager()

    class Meta:
        # TODO Generate "db_table" out of the class name.
        abstract = True
        managed = False
        base_manager_name = "objects"


def model_with_udf_manager(model_class):
    class Proxy(model_class):
        objects = TableFunctionManager()

        class Meta:
            proxy = True
            # TODO Really not necessary?
            # app_label = model_class._meta.app_label

    return Proxy
