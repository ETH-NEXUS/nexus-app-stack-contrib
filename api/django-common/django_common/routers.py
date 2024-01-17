from django_common.utilities import call_all_except_first_base_class_methods_until_not_none


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
        return False


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
        return call_all_except_first_base_class_methods_until_not_none(self, "db_for_read", model,
                                                                       **hints)

    def db_for_write(self, model, **hints):
        return call_all_except_first_base_class_methods_until_not_none(self, "db_for_write", model,
                                                                       **hints)

    def allow_relation(self, obj1, obj2, **hints):
        return call_all_except_first_base_class_methods_until_not_none(self, "allow_relation", obj1,
                                                                       obj2, **hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return call_all_except_first_base_class_methods_until_not_none(self, "allow_migrate", db,
                                                                       app_label, model_name, **hints)
