from django.db import connections

from django_notification.management.commands.notify import COMMAND_NAME, Command as NotifyCommand


class Command(NotifyCommand):

    def get__file__(self):
        return __file__

    def handle(self, *args, **options):
        connection = connections["import"].cursor().connection
        connection.execute(f"LISTEN command__{options[COMMAND_NAME]}")
        notifies = connection.notifies()

        while not self.call(options, connection):
            next(notifies)
