import django.db.models.options as options

from django_notification.emailer import Emailer as DefaultEmailer

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("app_label_routing",)

Emailer = DefaultEmailer()
