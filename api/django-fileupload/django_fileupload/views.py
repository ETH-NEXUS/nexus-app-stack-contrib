import os
from os import path

from django.http import FileResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django.utils import timezone

from django_common.postgresql import exclusive_insert_table_lock
from django_common.renderers import PassthroughRenderer
from django_fileupload.models import FileUpload, FileUploadBatch
from django_fileupload.serializers import (DrfYasgWorkaroundFileUploadBatchSerializer, FileUploadBatchSerializer,
                                           FileUploadSerializer)
from python_utilities.crypto import generate_checksum_from_chunks


class FileUploadBatchViewSet(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = FileUploadBatch.objects.all()
    serializer_class = FileUploadBatchSerializer
    parser_classes = (MultiPartParser,)
    has_owner = True
    # Maximum file size in bytes. For example 5 * 1024 * 1024 is 5 MB.

    def get_max_file_size(self, request):
        return None

    # Workaround for "drf-yasg" (see https://github.com/axnsan12/drf-yasg/issues/503).
    def get_serializer_class(self):
        if self.action == "create":
            return DrfYasgWorkaroundFileUploadBatchSerializer
        return self.serializer_class

    def add_metadata(self, request, file_upload_batch):
        pass

    def verify_file_extension(self, request, file_position, file_name_parts):
        return True

    def verify_file_checksum(self, request, file_position, file_name_parts, file_checksum):
        return True

    def verify_file_count(self, request, count):
        return True

    def create(self, request, *args, **kwargs):
        if request.FILES:
            files = request.FILES.getlist("files")
            if self.verify_file_count(request, len(files)):
                for file_position, file in enumerate(files):

                    if self.get_max_file_size(request) and file.size > self.get_max_file_size(request):
                        raise ValidationError(_(f"File size exceeds the maximum allowed size of {self.get_max_file_size(request) / (1024 ** 2)} MB."))

                    file_name_parts = os.path.splitext(file.name)
                    if self.verify_file_extension(request, file_position, file_name_parts):
                        if self.verify_file_checksum(request, file_position, file_name_parts,
                                                     generate_checksum_from_chunks(file.chunks())):
                            continue
                        raise ValidationError(_("Incorrect or no checksums in the request."))
                    raise ValidationError(_("Files with incorrect extension in the request."))
                response = []
                with exclusive_insert_table_lock(FileUploadBatch):
                    if self.has_owner:
                        file_upload_batch = FileUploadBatch.objects.create(owner=request.user)
                    else:
                        file_upload_batch = FileUploadBatch.objects.create()
                    # Metadata needs to be added here as FileUpload.objects.create(...) may depend on it.
                    self.add_metadata(request, file_upload_batch)
                    for file_position, file in enumerate(files):
                        file_upload = FileUpload.objects.create(
                            file_upload_batch=file_upload_batch,
                            position=file_position,
                            file=file,
                        )
                        response.append({'id': file_upload.id, 'name': file_upload.name})

                    return Response(response, status=status.HTTP_201_CREATED)
            raise ValidationError(_("Incorrect number of files in the request."))
        raise ValidationError(_("No files in the request."))


class FileDownloadViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer

    @action(detail=True, methods=("get",), renderer_classes=(PassthroughRenderer,))
    def download(self, request, *args, **kwargs):
        file_upload = self.get_object()
        response = FileResponse(file_upload.file.open(), content_type=file_upload.detected_mime_type)
        response["Content-Length"] = file_upload.file.size
        response["Content-Disposition"] = 'attachment; filename="%s"' % path.basename(file_upload.file.name)
        return response


class FileUploadViewSet(
    FileDownloadViewSet,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def keep_after_deletion(self):
        return False

    def destroy(self, request, *args, **kwargs):
        file_upload = self.get_object()
        if self.keep_after_deletion():
            file_upload.deleted_on = timezone.now()
            file_upload.save()
        else:
            file_upload.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    pass
