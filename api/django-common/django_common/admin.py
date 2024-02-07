from django.contrib import admin


def create_model_admin(model_admin, name, model, verbose_name=None, verbose_name_plural=None):
    class Meta:
        proxy = True
        app_label = model_admin.__module__[:model_admin.__module__.index(".")]

    if verbose_name is not None:
        Meta.verbose_name = verbose_name
    if verbose_name_plural is not None:
        Meta.verbose_name_plural = verbose_name_plural

    new_model = type(name, (model,), {"__module__": "", "Meta": Meta})
    admin.site.register(new_model, model_admin)
    return model_admin


class EditableFieldsTabularInline(admin.TabularInline):
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
