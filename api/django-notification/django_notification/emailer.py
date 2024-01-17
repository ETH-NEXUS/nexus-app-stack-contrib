import logging
import re
from datetime import datetime
from email.mime.image import MIMEImage
from os import environ

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

SEND_MAILS = environ.get("DJANGO_NOTIFICATION_SEND_MAILS", "False") == "True"


class Emailer:
    def _depth_first_search(self, node_list, got_it):
        for node in node_list:
            if got_it(node):
                return node
            elif hasattr(node, "nodelist"):
                return self._depth_first_search(node.nodelist, got_it)

    def send_using_template(self, subject, template_name, context, images, cc_emails, to_emails):
        template = get_template(template_name)
        if subject is None:
            title_node = self._depth_first_search(template.template.nodelist,
                                                  lambda n: isinstance(n, BlockNode) and n.name == "title")
            if title_node is not None:
                subject = re.sub("<.*?>", "", title_node.render(Context(context)))
        self.send(subject, template.render(context), images, cc_emails, to_emails)

    def send(self, subject, html_message, images, cc_emails, to_emails):
        logger.debug(f"Sending email with subject {subject} from {settings.EMAIL_FROM} to {to_emails}, cc {cc_emails}.")
        if SEND_MAILS:
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=strip_tags(html_message),
                from_email=settings.EMAIL_FROM,
                to=to_emails,
                cc=cc_emails,
            )
            email_message.attach_alternative(html_message, "text/html")

            for cid, image in images:
                mime_image = MIMEImage(image)
                mime_image.add_header("Content-ID", f"<{cid}>")
                email_message.attach(mime_image)

            number_email_sent = email_message.send()
        else:
            number_email_sent = len(to_emails)

        from .models import SentEmail
        SentEmail.objects.create(
            from_email=settings.EMAIL_FROM,
            to_emails=", ".join(to_emails),
            cc_emails=", ".join(cc_emails),
            subject=subject,
            html_message=html_message,
            sent_at=datetime.now() if number_email_sent > 0 else None,
        )
