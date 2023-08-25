# Generated by Django 4.2.4 on 2023-08-25 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_fileupload', '0003_alter_fileupload_batch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fileupload',
            old_name='hash',
            new_name='checksum',
        ),
        migrations.RenameField(
            model_name='fileupload',
            old_name='batch',
            new_name='file_upload_batch',
        ),
        migrations.AddField(
            model_name='fileupload',
            name='position',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='fileupload',
            constraint=models.UniqueConstraint(fields=('file_upload_batch', 'position'), name='unique__position_in_a_file_upload_batch'),
        ),
    ]
