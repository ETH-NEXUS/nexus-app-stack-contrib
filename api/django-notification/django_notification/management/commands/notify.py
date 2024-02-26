import traceback

from django.core.management import BaseCommand, call_command
from django.db import connections

from django_notification import Emailer

PROJECT_NAME = "project_name"
COMMAND_NAME = "command_name"
TO_EMAIL_ADDRESSES = "to_email_addresses"
CC_EMAIL_ADDRESSES = "cc_email_addresses"


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--%s" % PROJECT_NAME, required=True,
                            help="So that the recipient recognizes which project issued the notification.", type=str)
        parser.add_argument("--%s" % COMMAND_NAME, required=True, type=str)
        parser.add_argument("--%s" % TO_EMAIL_ADDRESSES, nargs="*", required=True, type=str)
        parser.add_argument("--%s" % CC_EMAIL_ADDRESSES, nargs="*", required=False, type=str, default=[])

    def call(self, options, database_connection=None):
        try:
            call_command(options[COMMAND_NAME], database_connection=database_connection)
            return True
        except BaseException as e:
            Emailer.send_using_template(
                None,
                "notifications/error_message.html",
                {
                    "project_name": options[PROJECT_NAME],
                    "program_name": options[COMMAND_NAME],
                    "error_message": traceback.format_exc(),
                },
                [],
                options[CC_EMAIL_ADDRESSES],
                options[TO_EMAIL_ADDRESSES],
            )
            traceback.print_exc()
            return False

    def handle(self, *args, **options):
        self.call(options)
