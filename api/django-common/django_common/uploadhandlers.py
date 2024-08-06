from os import environ

from django.conf import settings
from django.core.files.uploadhandler import (MemoryFileUploadHandler, StopUpload, TemporaryFileUploadHandler,
                                             UploadFileException)

"""
To replace the existing file upload handlers with these handlers, add the following to the settings.py file:

FILE_UPLOAD_HANDLERS = [
    "django_common.uploadhandlers.HardLimitMemoryFileUploadHandler",
    "django_common.uploadhandlers.HardLimitTemporaryFileUploadHandler",
]

And this to the Dockerfile:

ARG HARD_UPLOAD_SIZE_LIMIT=524288000
ENV DJANGO_HARD_UPLOAD_SIZE_LIMIT $HARD_UPLOAD_SIZE_LIMIT
"""

HARD_LIMIT = int(environ.get("DJANGO_HARD_UPLOAD_SIZE_LIMIT"))


def check(raw_data, start):
    if (start + len(raw_data)) < HARD_LIMIT:
        return True
    raise StopUpload()


class HardLimitMemoryFileUploadHandler(MemoryFileUploadHandler):
    """See also https://docs.djangoproject.com/en/5.0/ref/files/uploads/#module-django.core.files.uploadhandler"""

    if settings.FILE_UPLOAD_MAX_MEMORY_SIZE > HARD_LIMIT:
        raise UploadFileException()

    def receive_data_chunk(self, raw_data, start):
        if check(raw_data, start):
            return super().receive_data_chunk(raw_data, start)


class HardLimitTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """See also https://docs.djangoproject.com/en/5.0/ref/files/uploads/#module-django.core.files.uploadhandler"""

    def handle_raw_input(
        self, input_data, META, content_length, boundary, encoding=None
    ):
        if content_length <= HARD_LIMIT:
            return super().handle_raw_input(input_data, META, content_length, boundary, encoding)
        raise UploadFileException()

    def receive_data_chunk(self, raw_data, start):
        if check(raw_data, start):
            return super().receive_data_chunk(raw_data, start)
