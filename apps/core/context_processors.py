from apps.core.site_data import SITE_TAGLINE, SITE_TITLE, get_site_modules


def site_context(request):
    return {
        "site_title": SITE_TITLE,
        "site_tagline": SITE_TAGLINE,
        "site_modules": get_site_modules(),
    }
