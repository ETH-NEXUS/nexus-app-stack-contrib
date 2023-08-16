import os

from django.contrib.auth import get_user_model
from django.contrib.auth.management.commands import createsuperuser
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.db import transaction

PASSWORD_FIELD = createsuperuser.PASSWORD_FIELD
USER_PASSWORD_ENVIRONMENT_VARIABLE = "DJANGO_USER_PASSWORD"
GROUPS = "groups"


class Command(BaseCommand):
    """
    Example:
        # DJANGO_USER_PASSWORD=bar python -m django createuser --username foo --email foo@bar.baz --groups foo bar baz
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def add_arguments(self, parser):
        parser.add_argument("--%s" % self.UserModel.USERNAME_FIELD, required=True)
        for required_field in self.UserModel.REQUIRED_FIELDS:
            parser.add_argument("--%s" % required_field, required=True)
        parser.add_argument("--%s" % GROUPS, nargs="*")

    def handle(self, *args, **options):
        kwargs = {
            self.UserModel.USERNAME_FIELD: options[self.UserModel.USERNAME_FIELD],
            PASSWORD_FIELD: os.environ[USER_PASSWORD_ENVIRONMENT_VARIABLE],
        }
        for required_field in self.UserModel.REQUIRED_FIELDS:
            kwargs[required_field] = options[required_field]

        with transaction.atomic():
            user = self.UserModel.objects.create_user(**kwargs)

            for group in options[GROUPS]:
                group = Group.objects.get(name=group)
                user.groups.add(group)
