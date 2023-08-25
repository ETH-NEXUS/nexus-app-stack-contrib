import os

from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import User


class Command(createsuperuser.Command):

    def handle(self, *args, **options):
        if 'DJANGO_SUPERUSER_USERNAME' not in os.environ or User.objects.filter(
                username=os.getenv('DJANGO_SUPERUSER_USERNAME')).count() == 0:
            super().handle(*args, **options)
