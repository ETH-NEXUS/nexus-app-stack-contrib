# Django Notification

The following environment (<tt>.env</tt>) variables configure this app:

```
DJANGO_NOTIFICATION_SEND_MAILS=False
DJANGO_NOTIFICATION_TO_EMAIL_ADDRESSES=
DJANGO_NOTIFICATION_CC_EMAIL_ADDRESSES=
EMAIL_FROM=
```

The notification app requires a working message transfer agent (MTA) service. This can be archived with the following
Docker Compose configuration:

```
version: "3.9"

services:
  mta:
    image: bytemark/smtp
    platform: linux/amd64 # This prevents a warning message because there is no other build available.
    restart: unless-stopped
    env_file: .env
```

The following environment (<tt>.env</tt>) variables are used by the defined MTA service to relay received messages:

```
# Set to "localhost" in order to prevent unsuccessful logins on "smtp.ethz.ch".
RELAY_HOST=localhost
RELAY_PORT=587
RELAY_USERNAME=
RELAY_PASSWORD=
```

Finally, it needs to be defined how Django should handle emails by adding these lines to the <tt>settings.py</tt> file:

```
# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_FROM = environ.get("EMAIL_FROM")
EMAIL_HOST = "mta"
EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = EMAIL_FROM
```
