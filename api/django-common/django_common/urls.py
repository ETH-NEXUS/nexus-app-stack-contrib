import re

from django.contrib.admin.views.decorators import staff_member_required
from django.urls import re_path
from django.views.static import serve


# Copied from the django.conf.urls.static(...) function.
def static_path(prefix, view=serve, **kwargs):
    return (
        re_path(
            r"^%s(?P<path>.*)$" % re.escape(prefix.lstrip("/")), view, kwargs=kwargs
        ),
    )


@staff_member_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    """
    Example:
    urlpatterns = (...) + static_path(settings.MEDIA_URL, protected_serve, document_root=settings.MEDIA_ROOT)
    """
    return serve(request, path, document_root, show_indexes)
