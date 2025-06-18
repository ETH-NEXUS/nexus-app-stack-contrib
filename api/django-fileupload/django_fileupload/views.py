import os
from os import path

from django.http import FileResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from python_utilities.crypto import generate_checksum_from_chunks
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from django_common.postgresql import exclusive_insert_table_lock
from django_common.renderers import PassthroughRenderer
from django_fileupload.models import FileUpload, FileUploadBatch
from django_fileupload.serializers import (FileUploadBatchCreateSerializer, FileUploadBatchSerializer,
                                           FileUploadSerializer)


class FileUploadBatchViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = FileUploadBatch.objects.all()
    serializer_class = FileUploadBatchSerializer
    parser_classes = (MultiPartParser,)

    def get_serializer_class(self):
        if self.action == "create":
            return FileUploadBatchCreateSerializer
        return self.serializer_class

    def add_metadata(self, request, create_file_upload_batch):
        return create_file_upload_batch()

    def verify_file_extension(self, request, file_position, file_name_parts):
        return True

    def verify_file_name(self, request, file_position, file_name_parts, file_name):
        return True

    def verify_file_checksum(self, request, file_position, file_name_parts, file_checksum):
        return True

    def verify_file_count(self, request, count):
        return True

    @extend_schema(
        request=FileUploadBatchCreateSerializer,
        responses=FileUploadBatchSerializer,
    )
    def create(self, request, *args, **kwargs):
        if request.FILES:
            files = request.FILES.getlist("files")
            len_files = len(files)
            if self.verify_file_count(request, len_files):
                checksums = [None] * len_files
                for file_position, file in enumerate(files):
                    file_name_parts = os.path.splitext(file.name)
                    if self.verify_file_extension(request, file_position, file_name_parts):
                        if self.verify_file_name(request, file_position, file_name_parts, file.name):
                            checksum = generate_checksum_from_chunks(file.chunks())
                            if self.verify_file_checksum(
                                    request,
                                    file_position,
                                    file_name_parts,
                                    checksum
                            ):
                                checksums[file_position] = checksum
                                continue
                            raise ValidationError(_("Incorrect or no checksums in the request."))
                        raise ValidationError(_("Files with incorrect name in the request."))
                    raise ValidationError(_("Files with incorrect extension in the request."))
                response = []
                with exclusive_insert_table_lock(FileUploadBatch):
                    # Metadata needs to be added here as FileUpload.objects.create(...) may depend on it.
                    file_upload_batch = self.add_metadata(request,
                                                          lambda: FileUploadBatch.objects.create(owner=request.user))
                    for file_position, file in enumerate(files):
                        try:
                            file_upload = FileUpload.objects.get(file_upload_batch=file_upload_batch,
                                                                 position=file_position)
                            if checksums[file_position] == file_upload.checksum:
                                response.append({"id": file_upload.id, "name": file_upload.name})
                                continue
                            raise ValidationError(_("The checksum of a file in the current upload does not match the "
                                                    "checksum of the previously uploaded file at the same position."))
                        except FileUpload.DoesNotExist:
                            file_upload = FileUpload.objects.create(
                                file_upload_batch=file_upload_batch,
                                position=file_position,
                                file=file,
                            )
                            response.append({"id": file_upload.id, "name": file_upload.name})
                            continue
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
    pass
