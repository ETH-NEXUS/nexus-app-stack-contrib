from django.core.management.base import CommandError

from rest_framework.authtoken.management.commands import drf_create_token


class Command(drf_create_token.Command):
    def handle(self, *args, **options):
        """
        Copied from the rest_framework.authtoken.management.commands.drf_create_token.Command class.
        """
        username = options["username"]
        reset_token = options["reset_token"]

        try:
            token = self.create_user_token(username, reset_token)
        except drf_create_token.UserModel.DoesNotExist:
            raise CommandError(
                "Cannot create the Token: user {} does not exist".format(
                    username)
            )
        self.stdout.write(token.key)
