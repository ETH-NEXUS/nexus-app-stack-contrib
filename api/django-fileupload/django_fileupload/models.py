import os
from os.path import basename, join

import magic
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils import timezone

from django_common.models import OwnedModel
from python_utilities.crypto import generate_checksum_from_file


class FileUploadBatch(OwnedModel):
    uploaded_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        file_uploads_list = ", ".join(
            [os.path.basename(f.file.name) for f in FileUpload.objects.filter(
                file_upload_batch_id=self.id
            ).all()]
        )
        return f"Batch {self.id} ({file_uploads_list})"


class FileUploadFileStorage(FileSystemStorage):

    def get_alternative_name(self, file_root, file_ext):
        raise FileExistsError


def generate_file_path(instance):
    """Defines the file path to store the uploaded file to"""
    return instance.__class__.__name__


def _generate_complete_file_path(instance, filename):
    return join(generate_file_path(instance), str(instance.id), filename)


class FileUpload(models.Model):
    """
    Model to track file uploads.
    The model is an owned model means there is always an owner of the record
    which basically is the one that uploads the file
    """
    file_upload_batch = models.ForeignKey(
        FileUploadBatch, related_name="file_uploads", on_delete=models.CASCADE, null=False, blank=False
    )
    position = models.PositiveSmallIntegerField()
    file = models.FileField(upload_to=_generate_complete_file_path, storage=FileUploadFileStorage())
    detected_mime_type = models.CharField(max_length=100, editable=False)
    checksum = models.CharField(max_length=64, editable=False)

    def __str__(self):
        return self.file.path

    @property
    def name(self):
        return basename(self.file.name)

    @property
    def path(self):
        return self.file.path

    @property
    def size(self):
        return self.file.size

    def save(self, *args, **kwargs):
        # Overriding the function allows to use 'instance.id' in the 'file_path' function.
        if self.pk is None:
            tmp = self.file
            self.file = None
            super().save(*args, **kwargs)
            self.file = tmp
            super().save(update_fields=("file",))
        else:
            super().save(*args, **kwargs)
        self.checksum = generate_checksum_from_file(self.file.path)
        self.detected_mime_type = magic.from_file(self.path, mime=True)
        super().save(update_fields=("detected_mime_type", "checksum"))

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=("file_upload_batch", "position"),
                name="unique__position_in_a_file_upload_batch",
            ),
            # TODO Check if the file_upload_batch_position values are aligned.
        )
