from django.db import models


class SentEmail(models.Model):
    from_email = models.CharField(max_length=320, verbose_name="From")
    to_emails = models.CharField(max_length=320, verbose_name="Recipients")
    cc_emails = models.CharField(max_length=320, blank=True, null=True, verbose_name="CC Recipients")
    subject = models.TextField()
    html_message = models.TextField()
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label_routing = True
