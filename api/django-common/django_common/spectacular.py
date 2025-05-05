from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema

from .access import _get_access_object, _has_access, ADMIN_ACCESS, PRIVATE_ACCESS, PUBLIC_ACCESS


class CustomAutoSchema(AutoSchema):
    def get_tags(self):
        """
        Categorize endpoints based on the first meaningful path segment, ignoring "public" or "private" prefixes.
        """
        path = getattr(self.view, "request", None)
        if path and hasattr(path, "path"):
            path_segments = path.path[1:-1].split("/")
            if len(path_segments) > 1:
                if path_segments[1] in ("public", "private",):
                    if len(path_segments) > 2:
                        return (path_segments[2],)
                else:
                    return (path_segments[1],)

        return ("Uncategorized",)


_AUTH_EXTENSION = "x-access"
AUTH_EXTENSION_PRIVATE_ACCESS = {_AUTH_EXTENSION: str(PRIVATE_ACCESS)}
AUTH_EXTENSION_ADMIN_ACCESS = {_AUTH_EXTENSION: str(ADMIN_ACCESS)}


class CustomSchemaGenerator(SchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)

        # Filters out "/api/private/" endpoints for unauthenticated users.
        if request.user.is_authenticated:
            schema["paths"] = {
                path: data for path, data in schema["paths"].items() if not path.startswith("/api/public/")
            }
        else:
            schema["paths"] = {
                path: data for path, data in schema["paths"].items() if path.startswith("/api/public/")
            }

        # Remove lock symbol.
        for path, data in schema["paths"].items():
            if path.startswith("/api/public/"):
                for value in data.values():
                    value.pop("security", None)
                    if "parameters" in value:
                        value["parameters"] = [p for p in value["parameters"]
                                               if _has_access(
                                                   _get_access_object(p.pop(_AUTH_EXTENSION, str(PUBLIC_ACCESS))),
                                                   request
                                               )]
            else:
                for v in data.values():
                    if len(v["security"]) > 2:
                        v["security"].pop(2)

        # Remove the "/api" prefix from all endpoints for nicer OpenAPI UI URLs.
        schema["paths"] = {
           path[4:]: data for path, data in schema["paths"].items()
        }

        return schema
