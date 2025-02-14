from drf_spectacular.utils import extend_schema_view, extend_schema


def merge_parent_parameters(cls):
    """Collects OpenApiParameter annotations from all base classes of a given viewset class."""
    parameters = []
    for base in cls.__bases__:
        if hasattr(base, "filter_parameters"):
            parameters.extend(base.filter_parameters)
    return parameters


# Workaround to apply extend_schema_view with merged parameters from
# all inherited classes because django-spectacular does not support it
class AutoSchemaMixin:
    @classmethod
    def as_view(cls, *args, **initkwargs):
        # Merge parameters once at class definition time
        merged_parameters = merge_parent_parameters(cls)

        # Dynamically apply extend_schema_view with merged parameters
        cls = extend_schema_view(
            list=extend_schema(parameters=merged_parameters)
        )(cls)

        return super().as_view(*args, **initkwargs)
