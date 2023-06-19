# Generated by Django 4.2.2 on 2023-06-16 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_fileupload', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fileupload',
            name='name',
        ),
        migrations.RemoveField(
            model_name='fileupload',
            name='size',
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='hash',
            field=models.CharField(editable=False, max_length=64),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='mime_type',
            field=models.CharField(editable=False, max_length=100),
        ),
    ]
