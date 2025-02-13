from collections import OrderedDict

from django import forms
from django.contrib import messages
from django.contrib.admin import ModelAdmin
from django.contrib.messages import SUCCESS
from django.contrib.messages.storage import default_storage
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

    def save_form(self, request, form, change):
        self._saved = False
        new_object = super().save_form(request, form, change)

        if not hasattr(self, "_database_error"):
            try:
                self.save_model(request, new_object, form, change)
                if all_valid(self._formsets):
                    self.save_related(request, form, self._formsets, change)
                self._saved = True
            except DatabaseError as e:
                self._database_error = e
        if hasattr(self, "_database_error"):
            request_messages = messages.get_messages(request)
            if len(request_messages) > 0:
                request._messages = default_storage(request)
                for message in request_messages:
                    if message.level != SUCCESS:
                        messages.add_message(request, message.level, message.message, message.extra_tags)

            form.add_error(None, f"An error occurred: {str(self._database_error)}")
            del self._database_error

            # Hack: afterwards the all_valid(formsets) function is called in the ModelAdmin._changeform_view(...) method
            # and fails. As a result, the exception message is passed to the user interface.
            class Invalid(forms.Form):
                pass
            self._formsets.append(formset_factory(Invalid)())

        return new_object

    def save_model(self, request, obj, form, change):
        # At this point it is too late to handle database exceptions.
        if not self._saved:
            super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        # At this point it is too late to handle database exceptions.
        if not self._saved:
            super().save_related(request, form, formsets, change)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        try:
            return super().changeform_view(request, object_id, form_url, extra_context)
        except DatabaseError as e:
            self._database_error = e
            return super()._changeform_view(request, object_id, form_url, extra_context)

    def _create_formsets(self, request, obj, change):
        formsets, inline_instances = super()._create_formsets(request, obj, change)
        self._formsets = formsets # Hack
        return formsets, inline_instances


def model_with_udf_manager(model_class):
    class Proxy(model_class):
        objects = TableFunctionManager()

        class Meta:
            proxy = True
            # TODO Really not necessary?
            # app_label = model_class._meta.app_label

    return Proxy
