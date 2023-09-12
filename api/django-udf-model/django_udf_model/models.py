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
        if not hasattr(obj1, "using") and not hasattr(obj2, "using"):
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == "default":
            return True
        return False


class UdfModel(Model):
    function_args = OrderedDict()
    objects = TableFunctionManager()

    class Meta:
        abstract = True
        managed = False
        base_manager_name = "objects"
