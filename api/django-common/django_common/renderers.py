from rest_framework import renderers


class PassthroughRenderer(renderers.BaseRenderer):
    media_type = ""
    format = ""

    def render(self, data, **kwargs):
        return data
