from django.contrib import admin

from apps.books.models import Book, BookAsset, BookTag


class BookAssetInline(admin.TabularInline):
    model = BookAsset
    extra = 0


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "status",
        "visibility",
        "rating",
        "word_count",
        "updated_at",
    )
    list_filter = ("status", "visibility", "created_at", "updated_at")
    search_fields = ("title", "author", "publisher", "tag_links__name", "short_review")
    inlines = [BookAssetInline]


@admin.register(BookTag)
class BookTagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


@admin.register(BookAsset)
class BookAssetAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "book",
        "asset_type",
        "visibility",
        "download_enabled",
        "created_at",
    )
    list_filter = ("asset_type", "visibility", "download_enabled")
    search_fields = ("file_name", "book__title")
