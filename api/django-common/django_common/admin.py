from django.contrib import admin

from .clazz import create_dynamic_class


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

    new_model = create_dynamic_class(name, model, {"__module__": "", "Meta": Meta})
    admin.site.register(new_model, model_admin)
    return model_admin


def _extend_get_queryset_method(model_admin_class, filter_queryset):
    original_get_queryset = model_admin_class.get_queryset
    def new_get_queryset(self, request):
        queryset = original_get_queryset(self, request)
        queryset = filter_queryset(queryset, request)
        return queryset
    model_admin_class.get_queryset = new_get_queryset


def _whitelist_inline(get_filter_queryset_function):
    def decorator(model_admin_class):
        filter_queryset_function = get_filter_queryset_function(model_admin_class.model)

        if filter_queryset_function is not None:
            _extend_get_queryset_method(model_admin_class, filter_queryset_function)

            original_get_formset = model_admin_class.get_formset
            def new_get_formset(self, request, obj=None, **kwargs):
                formset = original_get_formset(self, request, obj, **kwargs)
                assert not hasattr(formset, "_request")
                formset._request = request
                return formset
            model_admin_class.get_formset = new_get_formset

            original_add_fields = model_admin_class.formset.add_fields
            def new_add_fields(self, form, index):
                # The super method must be called first, as this is where the "id" field is added to the form.
                result = original_add_fields(self, form, index)
                if index is not None:
                    id_field = form.fields["id"]
                    id_field.queryset = filter_queryset_function(id_field.queryset, self._request)
                return result
            model_admin_class.formset.add_fields = new_add_fields

        return model_admin_class
    return decorator


def register_and_whitelist(model, get_filter_queryset_function):
    def decorator(model_admin_class):
        admin.register(model)(model_admin_class)
        filter_queryset_function = get_filter_queryset_function(model)

        if filter_queryset_function is not None:
            _extend_get_queryset_method(model_admin_class, filter_queryset_function)

        for inline in model_admin_class.inlines:
            _whitelist_inline(get_filter_queryset_function)(inline)
        return model_admin_class
    return decorator


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
