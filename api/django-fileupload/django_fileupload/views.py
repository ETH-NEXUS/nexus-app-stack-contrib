from os import path

from django.http import FileResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from django_common.renderers import PassthroughRenderer
from django_fileupload.models import FileUpload, FileUploadBatch
from django_fileupload.serializers import FileUploadBatchSerializer, FileUploadSerializer


class FileUploadBatchViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = FileUploadBatch.objects.all()
    serializer_class = FileUploadBatchSerializer

    def add_metadata(self, request, file_upload_batch):
        pass

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist("files")
        if files:
            response = []
            batch = FileUploadBatch.objects.create(owner=request.user)
            self.add_metadata(request, batch)
            for file in files:
                file_upload = FileUpload.objects.create(batch=batch, file=file)
                response.append({'id': file_upload.id, 'name': file_upload.name})
            return Response(response, status=status.HTTP_201_CREATED)

        raise ValidationError(_("No files in the request."))


class FileUploadViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (IsAuthenticated,)
    queryset = FileUpload.objects.all()
    serializer_class = FileUploadSerializer

    @action(detail=True, methods=["get"], renderer_classes=(PassthroughRenderer,))
    def download(self, request, *args, **kwargs):
        file_upload: FileUpload = self.get_object()
        response = FileResponse(file_upload.file.open(), content_type=file_upload.mime_type)
        response["Content-Length"] = file_upload.file.size
        response["Content-Disposition"] = 'attachment; filename="%s"' % path.basename(file_upload.file.name)
        return response
