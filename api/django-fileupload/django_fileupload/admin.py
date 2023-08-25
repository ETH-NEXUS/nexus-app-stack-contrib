from datetime import datetime as dt

from django.contrib import admin
from hurry.filesize import size as hr_size

from .models import FileUpload

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


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


class FileUploadAdminInline(admin.TabularInline):
    model = FileUpload
    readonly_fields = ("mime_type", "checksum")

    def has_add_permission(self, request, obj):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FileUploadBatchAdmin(admin.ModelAdmin):
    inlines = (FileUploadAdminInline,)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
