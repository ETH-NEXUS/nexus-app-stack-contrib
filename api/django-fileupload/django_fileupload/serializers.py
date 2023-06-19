from rest_framework import serializers
from models import FileUpload, FileUploadBatch


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload record
    """

    class Meta:
        model = FileUpload
        fields = "__all__"


class FileUploadBatchSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload batch record
    """

    files = FileUploadSerializer(many=True)

    class Meta:
        model = FileUploadBatch
        fields = "__all__"
