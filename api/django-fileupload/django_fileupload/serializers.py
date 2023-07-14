from rest_framework import serializers

from django_fileupload.models import FileUpload, FileUploadBatch


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload record
    """

    class Meta:
        model = FileUpload
        fields = ("id", "name")


class FileUploadBatchSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload batch record
    """

    files = FileUploadSerializer(source='fileupload_set', many=True)

    class Meta:
        model = FileUploadBatch
        fields = ("id", "uploaded_on", "files")
