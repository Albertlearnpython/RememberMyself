from django.contrib import admin

from apps.articles.models import ArticleEntry


@admin.register(ArticleEntry)
class ArticleEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "visibility", "source_filename", "updated_at")
    list_filter = ("visibility",)
    search_fields = ("title", "summary", "markdown_content", "source_filename")

