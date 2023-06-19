from django.contrib import admin
from datetime import datetime as dt
from hurry.filesize import size as hr_size

from .models import FileUploadBatch, FileUpload

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


@admin.register(FileUploadBatch)
class FileUploadBatchAdmin(admin.ModelAdmin):
    pass


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "uploaded_by",
        "uploaded_on",
        "mime_type",
        "hr_size",
        "hash",
    )

    def hr_size(self, file_upload: FileUpload):
        return hr_size(file_upload.size)

    hr_size.short_description = "Size"

    def uploaded_on(self, file_upload: FileUpload):
        return dt.strftime(file_upload.batch.uploaded_on, DATE_TIME_FORMAT)

    uploaded_on.short_description = "Uploaded on"

    def uploaded_by(self, file_upload: FileUpload):
        return file_upload.batch.owner

    uploaded_by.short_description = "Uploaded by"
