from django.http import Http404
from django.shortcuts import render

from apps.core.site_data import get_site_modules


def placeholder(request, module_key):
    modules = {module["key"]: module for module in get_site_modules()}
    module = modules.get(module_key)
    if module is None:
        raise Http404("Module not found")

    context = {
        "module": module,
        "page_title": module["title"],
    }
    return render(request, "core/placeholder.html", context)
