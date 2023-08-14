import hashlib
import os
from os.path import basename, join

import magic
from django.db import models
from django.utils import timezone

from django_common.models import OwnedModel

BUFFER_SIZE = 65536


class FileUploadBatch(OwnedModel):
    uploaded_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (f"Batch {self.id} ("
                + " ".join([os.path.basename(f.file.name) for f in FileUpload.objects.filter(batch_id=self.id).all()])
                + ")")


def file_path(instance, filename):
    """Defines the filepath to store the uploaded file to"""
    return join(instance.__class__.__name__, str(instance.id), filename)


class FileUpload(models.Model):
    """
    Model to track file uploads.
    The model is an owned model means there is always an owner of the record
    which basically is the one that uploads the file
    """
    batch = models.ForeignKey(
        FileUploadBatch, related_name="file_uploads", on_delete=models.CASCADE, null=False, blank=False
    )
    file = models.FileField(upload_to=file_path)
    mime_type = models.CharField(max_length=100, editable=False)
    hash = models.CharField(max_length=64, editable=False)

    def __str__(self):
        return self.file.path

    def calculate_hash(self):
        """Calculates the hash of the own file"""
        sha256 = hashlib.sha256()

        with open(self.file.path, "rb") as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                sha256.update(data)
        return sha256.hexdigest()

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
            super().save(update_fields=["file"])
        else:
            super().save(*args, **kwargs)
        self.hash = self.calculate_hash()
        self.mime_type = magic.from_file(self.path, mime=True)
        super().save(update_fields=["hash", "mime_type"])
