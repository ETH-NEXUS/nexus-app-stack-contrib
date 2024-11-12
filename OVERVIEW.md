# API (application programming interface)

| Directory/File                    | Description                            | Example/Detail                                                                        |
|-----------------------------------|----------------------------------------|---------------------------------------------------------------------------------------|
| `django_common/admin.py`          | Helpers in dealing with admin models   | Create multiple admin models for one model, read-only admin models by default, ...    |
| `django_common/authorization.py`  | Helpers for authorization              | Extra `permission_classes`, model mixin for authorization                             |
| `django_common/clazz.py`          | Class utilities                        | Call methods of the same name in all base classes, ...                                |
| `django_common/fixtures.py`       | Helpers for Django fixtures            | Annotations that provide a nice way to modify a fixtures import                       |
| `django_common/models.py`         | Predefined common models               | Cantons of Switzerland, common bioinformatic MIME types, ...                          |  
| `django_common/postgresql.py`     | Helpers for PostgreSQL                 | Annotations for synchronizing the database access (`LOCK TABLE`)                      |
| `django_common/renderers.py`      | Uncommon versions                      | Render binary files                                                                   |
| `django_common/routers.py`        | Extra kinds of routers                 | Use a different database backend like SQLite for a specific app e.g. notification     |
| `django_common/run.py`            | Functions that run code                | Function that run a coroutine synchronously                                           |
| `django_common/serializers.py`    | Predefined model serializer            | Serializer for the default Django user model                                          |
| `django_common/string.py`         | String manipulation functions          | Convert a CamelCase to a snake_case string                                            |
| `django_common/tests.py`          | Objects useful for testing             | Tests should use the existing database                                                |
| `django_common/uploadhandlers.py` | Extended default upload handlers       | Upload handlers with a hard upload size limit                                         |
| `django_common/urls.py`           | Helpers for defining URL patterns      | Configure and protect static paths, define paths according to the view class names    |
| `django_common/views.py`          | Mixins for views                       | Mixin that bakes together Swagger filter mixins with annotations (cake pattern)       |
| `django_common/management/`       | Helpful management commands            | Only create superuser if it does not already exist (prevents error messages)          |
| `django_fileupload/`              | Provides basic file uploading features | Extendable classes that implement a file upload based on files and file batches       |
| `django_fileupload/management/`   | File upload garbage collector          | Finds zombies by comparing the file system with the database (uploads are not atomic) |
| `django_notification/`            | Provides mail notification features    | Renders emails according to a template and sends + persists them in the database      |
| `django_notification/management/` | Executes a command with supervision    | A failed command triggers a notification and restarts it once the problem is resolved |
| `django_udf_model/`               | Another Django model abstraction       | A model based on user-defined database functions (UDFs) instead of tables             |

# UI (user interface)

| Directory/File    | Description                       | Example/Detail                                                          |
|-------------------|-----------------------------------|-------------------------------------------------------------------------|
| `vue-fileupload/` | Advanced file upload form element | Uploading file batches, progress bar, remove recent uploaded files, ... |
| `vue-viewer/`     | File viewer in the browser        | Supports text, PDF, pictures, videos, ...                               |

# CLI (command-line interface)

| Directory/File                   | Description               | Example/Detail                                                             |
|----------------------------------|---------------------------|----------------------------------------------------------------------------|
| `python_utilities/crypto.py`     | Cryptographic functions   | Compute the checksum of a file                                             |
| `python_utilities/filesystem.py` | File system navigation    | Get the absolute path of the Python script that uses this script           |
| `python_utilities/lazy.py`       | Lazy-init data structures | Initialization when accessing e.g. loading static values from the database |
