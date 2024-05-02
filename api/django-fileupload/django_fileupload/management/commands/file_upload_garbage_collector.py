import os
import shutil

from django.core.management import BaseCommand

from django_fileupload.models import FileUpload

FILE_UPLOAD_DIRECTORY = "file_upload_directory"
FILE_UPLOAD_GARBAGE_DIRECTORY = "file_upload_garbage_directory"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("--%s" % FILE_UPLOAD_DIRECTORY, required=True, type=str)
        parser.add_argument("--%s" % FILE_UPLOAD_GARBAGE_DIRECTORY, required=False, type=str)

    def find(self, absolute_directory, directory, *applies):
        for test in os.listdir(absolute_directory):
            absolute_test = os.path.join(absolute_directory, test)
            if os.path.isdir(absolute_test):
                self.find(absolute_test, test, *applies)
                continue
            for apply in applies:
                apply(absolute_directory, directory)

    def handle(self, *args, **options):
        queryset = FileUpload.objects

        def test_for_database_zombie(absolute_file_upload_directory, file_upload_directory):
            nonlocal queryset
            queryset = queryset.exclude(id=file_upload_directory)

        def test_for_filesystem_zombie(absolute_file_upload_directory, file_upload_directory):
            try:
                FileUpload.objects.get(pk=file_upload_directory)
            except FileUpload.DoesNotExist:
                print("Filesystem zombie:", absolute_file_upload_directory)
                relative_file_upload_directory = os.path.relpath(absolute_file_upload_directory,
                                                                 options[FILE_UPLOAD_DIRECTORY])
                if options[FILE_UPLOAD_GARBAGE_DIRECTORY]:
                    absolute_file_upload_garbage_directory = os.path.join(options[FILE_UPLOAD_GARBAGE_DIRECTORY],
                                                                          os.path.split(relative_file_upload_directory)[0])
                    os.makedirs(absolute_file_upload_garbage_directory, exist_ok=True)
                    print("Move", absolute_file_upload_directory, "to the garbage directory",
                          absolute_file_upload_garbage_directory)
                    shutil.move(absolute_file_upload_directory, absolute_file_upload_garbage_directory)

        self.find(options[FILE_UPLOAD_DIRECTORY], None, test_for_database_zombie,
                  test_for_filesystem_zombie)

        for file_upload in queryset.all():
            print("Database zombie:", file_upload)
