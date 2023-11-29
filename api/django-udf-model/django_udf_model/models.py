from django.db.models import Model
from collections import OrderedDict
from .query import TableFunctionManager


class UdfConnectionRouter:
    def db_for_read(self, model, **hints):
        if hasattr(model, "using"):
            return model.using
        return "default"

    def db_for_write(self, model, **hints):
        if hasattr(model, "using"):
            return model.using
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return True
        return False


class UdfModel(Model):
    using = "udf"
    function_args = OrderedDict()
    objects = TableFunctionManager()

    class Meta:
        # TODO Generate "db_table" out of the class name.
        abstract = True
        managed = False
        base_manager_name = "objects"
