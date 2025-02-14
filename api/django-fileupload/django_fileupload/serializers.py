from rest_framework import serializers

from django_fileupload.models import FileUpload, FileUploadBatch


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload record.
    """
    name = serializers.CharField(read_only=True)

    class Meta:
        model = FileUpload
        fields = ("id", "name", "checksum")


class FileUploadBatchSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload batch record.
    """

    file_uploads = FileUploadSerializer(read_only=True, many=True)

    class Meta:
        model = FileUploadBatch
        fields = ("file_uploads",)


class FileUploadBatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadBatch
        fields = ("id",)