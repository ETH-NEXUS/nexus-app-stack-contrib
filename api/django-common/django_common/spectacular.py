from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.openapi import AutoSchema


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


class CustomSchemaGenerator(SchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)

        # Filters out "/api/private/" endpoints for unauthenticated users.
        if request and not request.user.is_authenticated:
            schema["paths"] = {
                path: data for path, data in schema["paths"].items() if path.startswith("/api/public/")
            }

        # Remove lock symbol.
        for path, data in schema["paths"].items():
            if path.startswith("/api/public/"):
                for v in data.values():
                    v.pop("security", None)

        # Remove the "/api" prefix from all endpoints for nicer OpenAPI UI URLs.
        schema["paths"] = {
           path[4:]: data for path, data in schema["paths"].items()
        }

        return schema
