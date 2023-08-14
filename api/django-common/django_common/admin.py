from django.contrib import admin


def create_model_admin(model_admin, name, model, verbose_name=None, verbose_name_plural=None):
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    if verbose_name is not None:
        Meta.verbose_name = verbose_name
    if verbose_name_plural is not None:
        Meta.verbose_name_plural = verbose_name_plural

    new_model = type(name, (model,), {"__module__": "", "Meta": Meta})
    admin.site.register(new_model, model_admin)
    return model_admin
