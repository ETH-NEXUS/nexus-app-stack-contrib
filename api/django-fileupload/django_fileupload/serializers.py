from rest_framework import serializers

from django_fileupload.models import FileUpload, FileUploadBatch


class FileUploadSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload record.
    """

    class Meta:
        model = FileUpload
        fields = ("id", "name", "checksum", "deleted_on")


class FileUploadBatchSerializer(serializers.ModelSerializer):
    """
    Default serializer for a file upload batch record.
    """

    file_uploads = FileUploadSerializer(read_only=True, many=True)

    class Meta:
        model = FileUploadBatch
        fields = ("file_uploads",)


class DrfYasgWorkaroundFileUploadBatchSerializer(serializers.ModelSerializer):
    """
    Swagger workaround serializer for a file upload batch record.
    """

    # TODO Does not work with Swagger.
    # file_uploads = FileUploadSerializer(read_only=True, many=True)

    class Meta:
        model = FileUploadBatch
        fields = ()
