from collections import OrderedDict

from django import forms
from django.contrib.admin import ModelAdmin
from django.db import DatabaseError
from django.db.models import Model
from django.forms import formset_factory
from django.forms.formsets import all_valid

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


class UdfModelAdmin(ModelAdmin):
    _formsets = None

    def _create_formsets(self, request, obj, change):
        formsets, inline_instances = super()._create_formsets(request, obj, change)
        self._formsets = formsets # Hack
        return formsets, inline_instances

    def save_form(self, request, form, change):
        new_object = super().save_form(request, form, change)
        try:
            new_object.save()
            if all_valid(self._formsets):
                form.save_m2m()
                for formset in self._formsets:
                    self.save_formset(request, form, formset, change=change)
        except DatabaseError as e:
            # Hack: afterwards the all_valid(formsets) function is called in the ModelAdmin._changeform_view(...) method
            # and fails. As a result, the exception message is passed to the user interface.
            form.add_error(None, f"An error occurred: {str(e)}")
            class Invalid(forms.Form):
                pass
            self._formsets.append(formset_factory(Invalid)())
        return new_object

    def save_model(self, request, obj, form, change):
        # At this point it is too late to handle database exceptions.
        pass

    def save_related(self, request, form, formsets, change):
        # At this point it is too late to handle database exceptions.
        pass

    # TODO Use or remove.
    # def response_add(self, request, obj, post_url_continue=None):
    #     from django.contrib import messages
    #     m = messages.get_messages(request)
    #     for message in m:
    #         if message.level == messages.ERROR:
    #             m.used = False
    #             return self.response_post_save_add(request, obj)
    #     return super().response_add(request=request, obj=obj, post_url_continue=post_url_continue)
    #
    # def response_change(self, request, obj):
    #     from django.contrib import messages
    #     m = messages.get_messages(request)
    #     for message in m:
    #         if message.level == messages.ERROR:
    #             m.used = False
    #             return self.response_post_save_change(request, obj)
    #     return super().response_change(request=request, obj=obj)


def model_with_udf_manager(model_class):
    class Proxy(model_class):
        objects = TableFunctionManager()

        class Meta:
            proxy = True
            # TODO Really not necessary?
            # app_label = model_class._meta.app_label

    return Proxy
