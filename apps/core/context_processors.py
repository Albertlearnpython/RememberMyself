import os
from functools import lru_cache
from pathlib import Path

from django.conf import settings

from apps.core.site_data import SITE_TAGLINE, SITE_TITLE, get_site_modules


STATIC_VERSION_FILES = (
    "site/styles.css",
    "site/app.js",
    "site/epub-reader.js",
)


@lru_cache(maxsize=1)
def _get_site_asset_version():
    forced_version = os.getenv("SITE_ASSET_VERSION", "").strip()
    if forced_version:
        return forced_version

    static_dir = Path(settings.BASE_DIR) / "static"
    mtimes = []
    for relative_path in STATIC_VERSION_FILES:
        file_path = static_dir / relative_path
        if file_path.exists():
            mtimes.append(str(int(file_path.stat().st_mtime)))

    return max(mtimes, default="1")


def site_context(request):
    if settings.DEBUG:
        _get_site_asset_version.cache_clear()

    return {
        "site_title": SITE_TITLE,
        "site_tagline": SITE_TAGLINE,
        "site_modules": get_site_modules(),
        "site_asset_version": _get_site_asset_version(),
    }
