# Generated by Django 5.0.1 on 2024-01-18 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SentEmail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_email', models.CharField(max_length=320, verbose_name='From')),
                ('to_emails', models.CharField(max_length=320, verbose_name='Recipients')),
                ('cc_emails', models.CharField(blank=True, max_length=320, null=True, verbose_name='CC Recipients')),
                ('subject', models.TextField()),
                ('html_message', models.TextField()),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
