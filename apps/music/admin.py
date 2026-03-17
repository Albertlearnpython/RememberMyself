from django.contrib import admin

from apps.music.models import MusicAsset, MusicTag, MusicTrack


@admin.register(MusicTag)
class MusicTagAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)


class MusicAssetInline(admin.TabularInline):
    model = MusicAsset
    extra = 0


@admin.register(MusicTrack)
class MusicTrackAdmin(admin.ModelAdmin):
    list_display = ("title", "artist", "album", "visibility", "updated_at")
    list_filter = ("visibility",)
    search_fields = ("title", "artist", "album", "short_review")
    inlines = [MusicAssetInline]


@admin.register(MusicAsset)
class MusicAssetAdmin(admin.ModelAdmin):
    list_display = ("file_name", "track", "visibility", "download_enabled", "created_at")
    list_filter = ("visibility", "download_enabled")
    search_fields = ("file_name", "track__title", "track__artist")
