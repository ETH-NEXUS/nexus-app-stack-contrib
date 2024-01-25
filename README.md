# NEXUS App Stack (contrib)

## Requirements

In order to be able to work with the NEXUS app stack code, the following requirements must be met.

### Repository access token

How to create a GitHub fine gained personal access token:

Go to https://github.com/settings/profile  
→ Developer settings  
→ Personal access tokens  
→ Fine-grained tokens  
→ Generate new token  
→ Choose as "Resource owner" "ETH-NEXUS"  
→ Select your project repository under "Only select repositories"  
→ Under "Repository permissions" change only "Contents" to "Read-only"

An owner of the ETH-NEXUS organization must approve your token request. Under https://github.com/orgs/ETH-NEXUS/people
you see who an owner is.

### Environment variables

Add the following environment variables to your <tt>.env</tt> file:

```
NEXUS_CONTRIB_REPOSITORY_TOKEN=
NEXUS_CONTRIB_REPOSITORY_BRANCH=github.com/ETH-NEXUS/nexus-app-stack-contrib.git@main
NEXUS_CONTRIB_DOWNLOAD_SCRIPT=raw.githubusercontent.com/ETH-NEXUS/nexus-app-stack-contrib/main/download.sh
```

### Docker Compose

Integrate the following lines in your common Docker Compose files version 3.9:

```
version: "3.9"

secrets:
  NEXUS_CONTRIB_REPOSITORY_TOKEN:
    environment: NEXUS_CONTRIB_REPOSITORY_TOKEN

services:
  service1:
    build:
      args:
        ENVIRONMENT: "Production"
        NEXUS_CONTRIB_REPOSITORY_BRANCH: "$NEXUS_CONTRIB_REPOSITORY_BRANCH"
        NEXUS_CONTRIB_DOWNLOAD_SCRIPT: "$NEXUS_CONTRIB_DOWNLOAD_SCRIPT"
      secrets:
        - NEXUS_CONTRIB_REPOSITORY_TOKEN
    volumes:
      - ${NEXUS_CONTRIB_BIND:-/dev/null:/.no_nexus_contrib_bind}
```

### Dockerfiles

The <tt>git</tt> command must be available during the Docker image build:

```
RUN apk add --update --no-cache git
```

**Note:** The Dockerfile commands like `COPY requirements.txt /` or `COPY app/package.json /app` has to be executed
before the commands relevant for the NEXUS app stack because it is useful that a dependency version update triggers an
update of the NEXUS app stack repository.

#### Python/Django (<tt>api</tt> subdirectory)

All NEXUS app stack libraries and/or apps that you want to use in the project are specified with the `PYTHONPATH`
environment variable.

```
ARG ENVIRONMENT
ARG NEXUS_CONTRIB_REPOSITORY_BRANCH
ARG NEXUS_CONTRIB_DOWNLOAD_SCRIPT
ENV PYTHONPATH="$PYTHONPATH:\
/nexus-app-stack-contrib/api/django-feature"
RUN --mount=type=secret,id=NEXUS_CONTRIB_REPOSITORY_TOKEN \
  export ENVIRONMENT=$ENVIRONMENT TOKEN=$(cat /run/secrets/NEXUS_CONTRIB_REPOSITORY_TOKEN) BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
  sh <(wget -q -O - --header="Authorization: Bearer $TOKEN" https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT || echo false) \
  $(echo ${PYTHONPATH//:\/nexus-app-stack-contrib\// })
```

**Note:** The command was tested with an Alpine Linux BusyBox Almquist shell.

See also the [Dockerfile.TINY_IMAGE](api/TEMPLATES/Dockerfile.TINY_IMAGE) template.

#### Vue/Quasar (<tt>ui</tt> subdirectory)

All NEXUS app stack packages that you want to use in the project are specified in the last line of the `RUN` command.

```
RUN --mount=type=secret,id=NEXUS_CONTRIB_REPOSITORY_TOKEN \
  export ENVIRONMENT=$ENVIRONMENT TOKEN=$(cat /run/secrets/NEXUS_CONTRIB_REPOSITORY_TOKEN) BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
  sh <(wget -q -O - --header="Authorization: Bearer $TOKEN" https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT || echo false) \
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
django-feature @ git+https://${NEXUS_CONTRIB_REPOSITORY_TOKEN}@${NEXUS_CONTRIB_REPOSITORY_BRANCH}#subdirectory=api/django-feature
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
git clone https://${NEXUS_CONTRIB_REPOSITORY_TOKEN}@github.com/ETH-NEXUS/nexus-app-stack-contrib.git -b main
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
TOKEN= \
  BRANCH=github.com/ETH-NEXUS/nexus-app-stack-contrib.git@main \
  sh download.sh api/django-feature
```
