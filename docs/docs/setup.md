---
title: Setup
---

# Setup
Follow the following steps to install the NEXUS App Stack Contrib in your project:


1. Clone the app stack contrib project locally into a folder next to your project folder
2. Add the following entries to your `.env` file:

    ```bash title=".env" linenums="1"
    # Replace with your branch
    NEXUS_CONTRIB_REPOSITORY_BRANCH=github.com/ETH-NEXUS/nexus-app-stack-contrib.git@main

    # This will be used to pull the latest `download.sh` script from the main branch. You may also apply your changes and use a different branch.
    NEXUS_CONTRIB_DOWNLOAD_SCRIPT=raw.githubusercontent.com/ETH-NEXUS/nexus-app-stack-contrib/main/download.sh

    # Location of your local app stack contrib for dev purposes
    # This enables you to make modifications to app stack contrib locally and see changes immediatlly in your project
    NEXUS_CONTRIB_BIND=../nexus-app-stack-contrib:/nexus-app-stack-contrib
    ```

3. Add the following entries to your django app service in your `docker-compose.yml`:

    ```yaml title="docker-compose.yml" linenums="1"
    services:
        api:
            build:
                args:
                    NEXUS_CONTRIB_REPOSITORY_BRANCH: "$NEXUS_CONTRIB_REPOSITORY_BRANCH"
                    NEXUS_CONTRIB_DOWNLOAD_SCRIPT: "$NEXUS_CONTRIB_DOWNLOAD_SCRIPT"
    ```

    This instructs docker to use these environment variables as arguments (so essentially environemnt variables that are accessible only during the build step of our docker image)

4. For production in for example `docker-compose.prod.yml` also introduce the following variable:

    ```yaml title="docker-compose.prod.yml" linenums="1"
    services:
        api:
            build:
                args:
                    NEXUS_CONTRIB_ENV: Production
    ```
    This will make sure some additional cleanup steps are taken while building the image for production.

5. Open the backend `Dockerfile` and add the following entries:

    ```dockerfile title="api/Dockerfile" linenums="1"
    # Towards the top of the file after the FROM statement and DCC_ENV definition
    ARG NEXUS_CONTRIB_ENV
    ARG NEXUS_CONTRIB_REPOSITORY_BRANCH
    ARG NEXUS_CONTRIB_DOWNLOAD_SCRIPT

    # Remove or add additional apps from app stack contrib here
    ENV PYTHONPATH="$PYTHONPATH:\
    /nexus-app-stack-contrib/cli/python-utilities:\
    /nexus-app-stack-contrib/api/django-fileupload:\
    /nexus-app-stack-contrib/api/django-common"


    ...

    COPY ./requirements.txt /


    ### Install app stack contrib
    ### Copy app stack contrib app to the local folder

    RUN curl -sSL https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT -o download_script.sh
    RUN export ENVIRONMENT=$NEXUS_CONTRIB_ENV BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
        bash download_script.sh $(echo "$PYTHONPATH" | sed "s/:\/nexus-app-stack-contrib\// /g")
    RUN rm download_script.sh


    RUN pip install -r /requirements.txt
    ```

6. Add the same app stack contrib django apps that you included in the Dockerfile also in the `requirements.txt` file:

    ```text title="api/requirements.txt" linenums="1"
    -e /nexus-app-stack-contrib/cli/python-utilities
    -e /nexus-app-stack-contrib/api/django-common
    -e /nexus-app-stack-contrib/api/django-fileupload
    ```

    !!! info

        `django_common` and `python_utilities` will most likely be needed for other apps such as the `django-fileupload`.

7. Open your `api/app/settings.py` and add the following entries under `INSTALLED_APPS`:

    ```python title="api/app/settings.py" linenums="1"
    INSTALLED_APPS = [
        ...
        "django_common",
        "django_fileupload",
    ]
    ```

8. Open one of your `urls.py` and introduce the new endpoints into your app:
    ```python title="urls.py" linenums="1"
    from django_fileupload.urls import router as file_upload_router

    urlpatterns = [
        path("api/v1/", include(file_upload_router.urls))
    ]
    ```

9. Add the admin entries:
    ```python title="admin.py" linenums="1"
    from django_fileupload.admin import FileUploadAdmin
    from django_fileupload.models import FileUpload

    admin.site.register(FileUpload, FileUploadAdmin)
    ```

You should now have the basic setup of the app stack contrib ready.