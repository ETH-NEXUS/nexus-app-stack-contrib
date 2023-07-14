from rest_framework.routers import DefaultRouter

from django_fileupload.views import FileUploadBatchViewSet, FileUploadViewSet

router = DefaultRouter()
router.register("fileupload", FileUploadViewSet, basename="fileupload")
router.register("fileuploadbatch", FileUploadBatchViewSet, basename="fileuploadbatch")
