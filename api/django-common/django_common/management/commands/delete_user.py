from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    """
    Example:
        # python -m django delete_user --username foo
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def add_arguments(self, parser):
        parser.add_argument("--%s" % self.UserModel.USERNAME_FIELD, required=True)

    def handle(self, *args, **options):
        user = self.UserModel.objects.get(username=options[self.UserModel.USERNAME_FIELD])
        user.delete()
