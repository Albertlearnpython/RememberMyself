from django.contrib import admin

from apps.scenery.models import SceneryEntry, SceneryPhoto


class SceneryPhotoInline(admin.TabularInline):
    model = SceneryPhoto
    extra = 0
    readonly_fields = ("original_filename", "width", "height", "taken_at")


@admin.register(SceneryEntry)
class SceneryEntryAdmin(admin.ModelAdmin):
    list_display = ("display_title", "place_name", "city", "captured_at", "visibility", "updated_at")
    list_filter = ("visibility", "city", "province")
    search_fields = ("title", "place_name", "city", "location_text", "short_note", "why_it_matters")
    inlines = [SceneryPhotoInline]


@admin.register(SceneryPhoto)
class SceneryPhotoAdmin(admin.ModelAdmin):
    list_display = ("entry", "original_filename", "taken_at", "width", "height", "sort_order")
    list_select_related = ("entry",)
    search_fields = ("entry__title", "original_filename")

