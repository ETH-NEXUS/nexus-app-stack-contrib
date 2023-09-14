from rest_framework import renderers


class PassthroughRenderer(renderers.BaseRenderer):
    media_type = "application/octet-stream"
    format = ""

    def render(self, data, **kwargs):
        return data
