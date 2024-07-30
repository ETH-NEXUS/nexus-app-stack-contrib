# NEXUS App Stack (contrib)

## Requirements

In order to be able to work with the NEXUS app stack code, the following requirements must be met.

### Environment variables

Add the following environment variables to your <tt>.env</tt> file:

```
NEXUS_CONTRIB_REPOSITORY_BRANCH=github.com/ETH-NEXUS/nexus-app-stack-contrib.git@main
NEXUS_CONTRIB_DOWNLOAD_SCRIPT=raw.githubusercontent.com/ETH-NEXUS/nexus-app-stack-contrib/main/download.sh
```

### Docker Compose

Integrate the following lines in your Docker Compose file version 3.9:

```
version: "3.9"

services:
  service1:
    build:
      args:
        ENVIRONMENT: "Production" # Only needs to be defined in your Docker Compose production file.
        NEXUS_CONTRIB_REPOSITORY_BRANCH: "$NEXUS_CONTRIB_REPOSITORY_BRANCH"
        NEXUS_CONTRIB_DOWNLOAD_SCRIPT: "$NEXUS_CONTRIB_DOWNLOAD_SCRIPT"
    volumes:
      - ${NEXUS_CONTRIB_BIND:-/dev/null:/.no_nexus_contrib_bind}
```

### Dockerfiles

#### Basics

* The <tt>git</tt> command must be available during the Docker image build. On Alpine Linux you can install Git with the
  following command:

  ```
  RUN apk add --update --no-cache git
  ```

* The Dockerfile commands like `COPY requirements.txt /` or `COPY app/package.json /app` has to be executed before the
  Dockerfile commands relevant for the NEXUS app stack because it is convenient that a dependency version update
  triggers a refresh of the NEXUS app stack repository.

#### Python/Django (<tt>api</tt> subdirectory)

All NEXUS app stack Python libraries and/or Django apps that you want to use in your project must be added to the
`PYTHONPATH` environment variable so that Python is aware of the sources. This variable is also used during the NEXUS
app stack bootstrap to download/clone the sources from the repository (see next step).

Define the environment:

```
ARG ENVIRONMENT
ARG NEXUS_CONTRIB_REPOSITORY_BRANCH
ARG NEXUS_CONTRIB_DOWNLOAD_SCRIPT
ENV PYTHONPATH="$PYTHONPATH:\
/nexus-app-stack-contrib/api/django-feature-1:\
/nexus-app-stack-contrib/api/django-feature-2"
```

NEXUS App Stack <tt>api</tt> bootstrap command for the...

* Alpine Linux BusyBox Almquist shell:

  ```
  RUN export ENVIRONMENT=$ENVIRONMENT BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
    sh <(wget -q -O - https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT || echo false) \
    $(echo "$PYTHONPATH" | sed "s/:\/nexus-app-stack-contrib\// /g")
  ```

  See also the [Dockerfile.TINY_IMAGE](api/TEMPLATES/Dockerfile.TINY_IMAGE) template.

* Bash shell:

  ```
  RUN export ENVIRONMENT=$ENVIRONMENT BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
    bash -c "$(wget -q -O - https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT || echo false)" '' \
    $(echo "$PYTHONPATH" | sed "s/:\/nexus-app-stack-contrib\// /g")
  ```

#### Vue/Quasar (<tt>ui</tt> subdirectory)

All NEXUS app stack UI packages that you want to use in the project are specified in the last line of the `RUN` command.

```
RUN export ENVIRONMENT=$ENVIRONMENT BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
  sh <(wget -q -O - https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT || echo false) \
  ui/vue-fileupload ui/vue-viewer
```

**Note:** The command was tested with an Alpine Linux BusyBox Almquist shell.

See also the [Dockerfile.TINY_IMAGE](ui/TEMPLATES/Dockerfile.TINY_IMAGE) template.

## Reference the code

### Python

You can reference NEXUS app stack code in the <tt>requirements.txt</tt> file like this:

```
-e /nexus-app-stack-contrib/api/django-feature
```

If you do not need to edit the code locally, you can reference it directly (in this case you do not actually need any
NEXUS app stack specific Dockerfile adjustments):

```
django-feature @ git+https://${NEXUS_CONTRIB_REPOSITORY_BRANCH}#subdirectory=api/django-feature
```

### JavaScript

You can reference NEXUS app stack code in the <tt>package.json</tt> file like this:

```
{
  "dependencies": {
    "@nexus-app-stack-contrib/vue-feature": "link:../nexus-app-stack-contrib/ui/vue-feature"
  }
}
```

Unfortunately, Yarn does not support references to repository subdirectories. Therefore, the NEXUS app stack specific
Dockerfile adjustments are always necessary.

In order that the linked package finds all its dependencies, an installation of these dependencies for each of the
linked package is necessary. This can be done in the <tt>entrypoint.sh</tt>:

```
#!/usr/bin/env sh

set -euo pipefail

yarn install --cwd /nexus-app-stack-contrib/ui/vue-feature
yarn install --cwd /nexus-app-stack-contrib/ui/vue-another-feature
yarn install --cwd /nexus-app-stack-contrib/ui/vue-yet-another-feature
yarn install

yarn dev --host 0.0.0.0 --port 8077
```

## Development

Clone the "nexus-app-stack-contrib" repository to a local directory next to your project repository directory:

```
git clone https://github.com/ETH-NEXUS/nexus-app-stack-contrib.git -b main
```

The repository directory will be bind into your Docker containers. This approach allows you to develop the app stack
part alongside your project code without having to commit and deploy every change. The following environment
(<tt>.env</tt>) variable defines this bind:

```
NEXUS_CONTRIB_BIND=../nexus-app-stack-contrib:/nexus-app-stack-contrib
```

## Testing

### <tt>download.sh</tt>

```
BRANCH=github.com/ETH-NEXUS/nexus-app-stack-contrib.git@main \
  sh download.sh api/django-feature
```
