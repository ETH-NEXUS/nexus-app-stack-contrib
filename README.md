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

### Local copy of the repository

Clone the "nexus-app-stack-contrib" repository to a local directory next to your project repository directory:

```
git clone https://${NEXUS_CONTRIB_REPOSITORY_TOKEN}@github.com/ETH-NEXUS/nexus-app-stack-contrib.git -b main
```

The repository directory will be bind into your Docker containers. This approach allows you to develop the app stack
part alongside your project code without having to commit every change.

## Adjustments to your project

### Environment variables

Add the following environment variables to your <tt>.env</tt> file:

```
NEXUS_CONTRIB_REPOSITORY_TOKEN=
NEXUS_CONTRIB_REPOSITORY_BRANCH=github.com/ETH-NEXUS/nexus-app-stack-contrib.git@main
NEXUS_CONTRIB_DOWNLOAD_SCRIPT=raw.githubusercontent.com/ETH-NEXUS/nexus-app-stack-contrib/main/download.sh
NEXUS_CONTRIB_BIND=../nexus-app-stack-contrib:/nexus-contrib
```

### Docker Compose

Integrate the following lines in your common Docker Compose files version 3.9:

```
version: "3.9"

services:
  service1:
    build:
      args:
        NEXUS_CONTRIB_REPOSITORY_BRANCH: "$NEXUS_CONTRIB_REPOSITORY_BRANCH"
        NEXUS_CONTRIB_DOWNLOAD_SCRIPT: "$NEXUS_CONTRIB_DOWNLOAD_SCRIPT"
      secrets:
        - NEXUS_CONTRIB_REPOSITORY_TOKEN
    volumes:
      - ${NEXUS_CONTRIB_BIND:-/dev/null:/.no_nexus_contrib_bind}

secrets:
  NEXUS_CONTRIB_REPOSITORY_TOKEN:
    environment: NEXUS_CONTRIB_REPOSITORY_TOKEN
```

### Dockerfiles

The <tt>git</tt> command must be available during the Docker image build:

```
RUN apk add --update --no-cache git
```

Additionally, integrate the following lines in your Dockerfiles:

```
ARG NEXUS_CONTRIB_REPOSITORY_BRANCH
ARG NEXUS_CONTRIB_DOWNLOAD_SCRIPT
RUN --mount=type=secret,id=NEXUS_CONTRIB_REPOSITORY_TOKEN \
    export TOKEN=$(cat /run/secrets/NEXUS_CONTRIB_REPOSITORY_TOKEN) BRANCH=$NEXUS_CONTRIB_REPOSITORY_BRANCH && \
    sh <(wget -q -O - --header="Authorization: token $TOKEN" https://$NEXUS_CONTRIB_DOWNLOAD_SCRIPT) \
    api/django-feature
```

All NEXUS contrib libraries and apps that you want to use in the project must be specified in the last line of the `RUN`
command.

The command like `COPY requirements.txt /` or `COPY app/package.json /app` has to be executed before the commands
relevant for the NEXUS app stack because a code version update must trigger an update of the NEXUS app stack repository.

## Reference code

### Python

You can reference NEXUS contrib code in the <tt>requirements.txt</tt> file like this:

```
django-feature @ file:///nexus-contrib/api/django-feature
```

If you do not need to edit the code locally, you can reference it directly:

```
django-feature @ git+https://${NEXUS_CONTRIB_REPOSITORY_TOKEN}@${NEXUS_CONTRIB_REPOSITORY_BRANCH}#subdirectory=api/django-feature
```

### JavaScript

You can reference NEXUS contrib code in the <tt>package.json</tt> file like this:

```
{
  "dependencies": {
    "@nexus-contrib/vue-feature": "link:/nexus-contrib/ui/vue-feature"
  }
}
```

Unfortunately, Yarn does not support references to repository subdirectories.
