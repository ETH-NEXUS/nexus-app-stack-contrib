import re

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import re_path
from django.views.static import serve
from rest_framework.routers import DefaultRouter

from .string import camel_case_class_to_snake_case_string


@staff_member_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    """
    Example:
        urlpatterns = (...) + static_path(settings.MEDIA_URL, protected_serve, document_root=settings.MEDIA_ROOT)
    """
    return serve(request, path, document_root, show_indexes)


# Copied from the django.conf.urls.static(...) function.
def static_path(prefix, view=serve, **kwargs):
    return (
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs
        ),
    )


class ViewSetClassNameBasedNameRouter(DefaultRouter):
    def get_default_basename(self, viewset):
        tmp = camel_case_class_to_snake_case_string(viewset)
        if tmp.endswith("_view_set"):
            return tmp[:-len("_view_set")]
        raise ValueError

    def registerViewSet(self, viewset, prefix = None):
        basename = self.get_default_basename(viewset)
        return self.register(f"{prefix + '/' if prefix else ''}{basename.replace('_', '/', 1)}", viewset, basename)


class ViewSetClassNameRouter(ViewSetClassNameBasedNameRouter):
    def __init__(self, schema, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.schema = schema

    def registerViewSet(self, viewset, prefix = None):
        assert prefix is None
        basename = self.get_default_basename(viewset)
        if basename.startswith(self.schema):
            return self.register(basename.replace(self.schema + "_", "", 1), viewset, basename)
        raise ValueError
