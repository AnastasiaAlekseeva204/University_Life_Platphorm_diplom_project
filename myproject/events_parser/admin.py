from django.contrib import admin
from .models import ParsedEvent


@admin.register(ParsedEvent)
class ParsedEventAdmin(admin.ModelAdmin):
    list_display = ("title", "date_at", "source_url", "updated_at")
    list_filter = ("date_at",)
    search_fields = ("title", "excerpt", "content_plain")
    readonly_fields = ("created_at", "updated_at", "source_url")
    fields = (
        "title",
        "source_url",
        "date_at",
        "excerpt",
        "content",
        "content_plain",
        "created_at",
        "updated_at",
    )
