from datetime import datetime as dt

from django.contrib import admin
from hurry.filesize import size as hr_size

from .models import FileUpload

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("name", "uploaded_by", "uploaded_on", "deleted_on", "detected_mime_type", "hr_size", "checksum")
    readonly_fields = ("deleted_on", "file_upload_batch", "position", "file", "detected_mime_type", "checksum")

    def hr_size(self, file_upload: FileUpload):
        return hr_size(file_upload.size)

    hr_size.short_description = "Size"

    def uploaded_on(self, file_upload: FileUpload):
        return dt.strftime(file_upload.file_upload_batch.uploaded_on, DATE_TIME_FORMAT)

    uploaded_on.short_description = "Uploaded on"

    def deleted_on(self, file_upload: FileUpload):
        if file_upload.deleted_on:
            return dt.strftime(file_upload.deleted_on, DATE_TIME_FORMAT)
        else:
            return "Not deleted"

    deleted_on.short_description = "Deleted on"

    def uploaded_by(self, file_upload: FileUpload):
        return file_upload.file_upload_batch.owner

    uploaded_by.short_description = "Uploaded by"

    def has_module_permission(self, request):
        return False


class FileUploadAdminInline(admin.TabularInline):
    model = FileUpload
    readonly_fields = ("detected_mime_type", "checksum")
    show_change_link = True

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
