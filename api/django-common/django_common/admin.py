from django.contrib import admin

from .clazz import create_anonymous_class


def create_model_admin(model_admin, name, model, verbose_name=None, verbose_name_plural=None):
    """
    Creates several admin models from one model class.
    """
    class Meta:
        proxy = True
        app_label = model_admin.__module__[:model_admin.__module__.index(".")]
        # TODO Check whether this is a wise solution.
        auto_created = True

    if verbose_name is not None:
        Meta.verbose_name = verbose_name
    if verbose_name_plural is not None:
        Meta.verbose_name_plural = verbose_name_plural

    new_model = create_anonymous_class(name, model, {"__module__": "", "Meta": Meta})
    admin.site.register(new_model, model_admin)
    return model_admin


class OnlyInlinesAreEditableModelAdmin(admin.ModelAdmin):
    """
    An admin model that is read-only with the exception of inlines.
    """
    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.readonly_fields = [f.name for f in obj.__class__._meta.fields if f.name != "id"]
        return self.readonly_fields


class EditableFieldsTabularInline(admin.TabularInline):
    """
    An admin inline model that is read-only by default.
    """
    editable_fields = ()
    exclude = ()

    def get_readonly_fields(self, request, obj=None):
        return (list(self.readonly_fields)
                + [field.name for field in self.model._meta.fields
                   if field.name not in self.editable_fields and field.name not in self.exclude])

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False
