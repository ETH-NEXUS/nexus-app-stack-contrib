from os import path
from rest_framework import mixins, viewsets, status
from rest_framework.serializers import ValidationError
from rest_framework.decorators import action
from django_common.renderers import PassthroughRenderer
from models import FileUploadBatch, FileUpload
from serializers import FileUploadBatchSerializer
from django.http import FileResponse
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _


class FileUploadBatchViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = FileUploadBatch.objects.all()
    serializer_class = FileUploadBatchSerializer

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        if files:
            batch = FileUploadBatch.objects.create(owner=request.user)
            for file in files:
                FileUpload.objects.create(batch=batch, file=file)
            return Response(status=status.HTTP_201_CREATED)
        else:
            raise ValidationError(_("No files in the request."))


class FileUploadViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    @action(detail=True, methods=["get"], renderer_classes=(PassthroughRenderer,))
    def download(self, request, *args, **kwargs):
        file_upload: FileUpload = self.get_object()
        response = FileResponse(
            file_upload.file.open(), content_type=file_upload.mime_type
        )
        response["Content-Length"] = file_upload.value.size
        response["Content-Disposition"] = 'attachment; filename="%s"' % path.basename(
            file_upload.value.name
        )
        return response
