# Generated by Django 4.2.2 on 2023-08-08 14:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_fileupload', '0002_remove_fileupload_name_remove_fileupload_size_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='batch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='file_uploads', to='django_fileupload.fileuploadbatch'),
        ),
    ]