from django.contrib import admin
from django.utils.html import mark_safe

from .models import SentEmail


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ("to_emails", "subject", "sent_at")
    search_fields = ("to_emails", "subject")
    ordering = ("-id",)
    readonly_fields = ("from_email", "to_emails", "cc_emails", "subject", "get_html_message", "sent_at")
    exclude = ("html_message",)

    def get_html_message(self, obj):
        return mark_safe(
            f"<div style='border: 1px solid #4c4c4c; box-shadow: 5px 10px #bbb; padding: 10px'>{obj.html_message}</div>"
        )

    get_html_message.short_description = "Message"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
