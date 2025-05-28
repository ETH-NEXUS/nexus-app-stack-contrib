---
title: File Upload App
---

### Features
The file upload app enables you to easily handle file uploads in your application. Whenever one or more files are uploaded using the file upload app a single batch entry is created and a set of file entries are created in their respective models.

The batches keep information about the `owner`, `upload date` and `references to the associated files`. The files, on the other hand, keep information about the `deletion date`, `referece to the file upload batch`, `position in the batch`, `file location`, `file type` and a `checksum`.

Uploading multiple files with the same name will cause the latest file with that name to be retrieved when retrieving files. Deleting the file will only delete the latest version of the file but the previous versions will be kept and will also be returned. Custom implementations are required to enable a different behavior (for example deleting files by name).

#### Anonymous Owners
In cases where an owner is not needed you simply extend the FileUploadBatchViewSet and set the `has_owner` property to `False`. This will result in the owner value being set to `None` in the database entries.

```python title="views.py"
from django_fileupload.views import FileUploadBatchViewSet

class CustomFileUploadBatchViewSet(FileUploadBatchViewSet):
    has_owner = True
```

!!! note

    In this case you also have to use your newly defined view class in your route definitions.


#### Max File Size
There might be cases where you want to provide a max file upload size per upload request. In such cases you can take a similar approach to the one above but instead of setting a flag you can implement the `get_max_file_size` method.

```python title="views.py"
from django_fileupload.views import FileUploadBatchViewSet

class CustomFileUploadBatchViewSet(FileUploadBatchViewSet):
    def get_max_file_size(self, request):

        # Extract data from the request object or do some other calculations

        if some_condition:
            # The max_file_size is in megabytes
            # The get_max_file_size should return bytes or None
            return max_file_size * 1024 * 1024
        else:
            return None
```

!!! warning "Large file protection"

    If a user uploads a very large file, our application may get overwhelmed while checking its size (as it would attempt to load it onto the file system before reading the size). Therefore, we need to introduce additional measures as described below.

Introduce custom file upload handlers by adding them to your `settings.py` using the following snippet:

```python title="settings.py"
FILE_UPLOAD_HANDLERS = [
    "django_common.uploadhandlers.HardLimitMemoryFileUploadHandler",
    "django_common.uploadhandlers.HardLimitTemporaryFileUploadHandler",
]
```

Furthermore, you must set the following argument and environment variable in your backend `Dockerfile`:

```dockerfile title="api/Dockerfile"
ARG HARD_UPLOAD_SIZE_LIMIT=524288000
ENV DJANGO_HARD_UPLOAD_SIZE_LIMIT $HARD_UPLOAD_SIZE_LIMIT
```
This will ensure that there is a global django upper size limit that will prevent users from uploading files larger than it.

#### Keeping Files After Deletion
To keep files after deletion we must overwrite the method `keep_after_deletion` of the `FileUploadViewSet` class:

```python title="views.py"
from django_fileupload.views import FileUploadViewSet

class CustomFileUploadViewSet(FileUploadViewSet):
    def keep_after_deletion(self):
        return True
```
!!! info "Listing only files that are not marked as deleted"

    To retrieve only files that have not been marked as deleted you need to provide custom logic in the list method of the FileUploadViewSet class.


#### Other Customizations
Other methods of the `FileUploadBatchViewSet` class and the `FileUploadViewSet` class may be overwriten or extended in order to provide more custom behavior and also for providing additional metadata.

### Setup
1. Add the following two apps under INSTALLED_APPS in settings.py:
```python
"django_common",
"django_fileupload",
```
2. The following three packages need to be added to the `requirements.txt` of your django project:
```text
-e /nexus-app-stack-contrib/cli/python-utilities
-e /nexus-app-stack-contrib/api/django-common
-e /nexus-app-stack-contrib/api/django-fileupload
```
3. Make sure to setup the `FileUploadBatchViewSet` and `FileUploadViewSet` class endpoints by importing their routers / urls and defining them in your own routes.

!!! info "Use Swagger"

    To help you with your debugging process and to enable you to better understand what are the available methods and routes use swagger in your project.