from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.scenery.forms import SceneryEditorForm
from apps.scenery.models import SceneryEntry, SceneryPhoto
from apps.scenery.services import resequence_photos


def index(request):
    return _render_scenery_page(request)


def detail(request, entry_id):
    return _render_scenery_page(request, selected_id=entry_id)


def create_entry(request):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    if request.method != "POST":
        return redirect(f"{reverse('scenery:index')}?editor=create")

    form = SceneryEditorForm(request.POST, request.FILES)
    if form.is_valid():
        entry = form.save()
        summary = form.upload_summary
        message = f"已加入“{entry.display_title}”。"
        detected = []
        if summary.get("detected_time"):
            detected.append("拍摄时间")
        if summary.get("detected_location"):
            detected.append("地点")
        if detected:
            message += f" 已自动识别{'、'.join(detected)}。"
        messages.success(request, message)
        return redirect("scenery:detail", entry_id=entry.pk)

    return _render_scenery_page(request, form=form, editor_mode="create")


def edit_entry(request, entry_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    entry = get_object_or_404(SceneryEntry, pk=entry_id)
    if request.method != "POST":
        return redirect(f"{reverse('scenery:detail', kwargs={'entry_id': entry.pk})}?editor=edit")

    form = SceneryEditorForm(request.POST, request.FILES, instance=entry)
    if form.is_valid():
        entry = form.save()
        summary = form.upload_summary
        message = f"“{entry.display_title}”已更新。"
        if summary.get("uploaded_count"):
            message += f" 新增 {summary['uploaded_count']} 张图片。"
        messages.success(request, message)
        return redirect("scenery:detail", entry_id=entry.pk)

    return _render_scenery_page(request, selected_id=entry.pk, form=form, editor_mode="edit")


def delete_entry(request, entry_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    entry = get_object_or_404(SceneryEntry, pk=entry_id)
    if request.method == "POST":
        title = entry.display_title
        for photo in entry.photos.all():
            photo.image.delete(save=False)
        entry.delete()
        messages.success(request, f"已删除“{title}”。")
    return redirect("scenery:index")


def delete_photo(request, photo_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    photo = get_object_or_404(SceneryPhoto.objects.select_related("entry"), pk=photo_id)
    entry = photo.entry
    if request.method == "POST":
        photo.image.delete(save=False)
        photo.delete()
        resequence_photos(entry)
        messages.success(request, "图片已删除。")
    return redirect("scenery:detail", entry_id=entry.pk)


def photo_image(request, photo_id):
    photo = get_object_or_404(SceneryPhoto.objects.select_related("entry"), pk=photo_id)
    if not photo.entry.is_visible_to(request.user):
        raise Http404("Photo not found")

    return FileResponse(
        photo.image.open("rb"),
        content_type="image/jpeg",
        filename=photo.original_filename or f"scenery-{photo.pk}.jpg",
    )


def _render_scenery_page(request, selected_id=None, form=None, editor_mode=None):
    visible_entries_qs = SceneryEntry.objects.visible_to_user(request.user).prefetch_related("photos")
    entries_qs = visible_entries_qs

    q = request.GET.get("q", "").strip()
    city = request.GET.get("city", "").strip()
    year = request.GET.get("year", "").strip()

    if q:
        entries_qs = entries_qs.filter(
            Q(title__icontains=q)
            | Q(place_name__icontains=q)
            | Q(location_text__icontains=q)
            | Q(city__icontains=q)
            | Q(province__icontains=q)
            | Q(short_note__icontains=q)
            | Q(why_it_matters__icontains=q)
            | Q(long_note__icontains=q)
        )
    if city:
        entries_qs = entries_qs.filter(city=city)
    if year.isdigit():
        entries_qs = entries_qs.filter(captured_at__year=int(year))

    entries = list(entries_qs.distinct())
    selected_entry = None
    if selected_id is not None:
        selected_entry = next((entry for entry in entries if entry.pk == selected_id), None)
        if selected_entry is None:
            raise Http404("Scenery entry not found")
    elif entries:
        selected_entry = entries[0]

    can_edit = _user_can_edit(request.user)
    if editor_mode is None:
        editor_mode = request.GET.get("editor")
    if not can_edit:
        editor_mode = None
    if editor_mode == "edit" and selected_entry is None:
        editor_mode = None

    if form is None:
        if editor_mode == "edit" and selected_entry is not None:
            form = SceneryEditorForm(instance=selected_entry)
        elif editor_mode == "create":
            form = SceneryEditorForm()

    location_filters = [
        value for value in dict.fromkeys(entry.city for entry in visible_entries_qs if entry.city)
    ]
    year_filters = [
        value for value in dict.fromkeys(entry.captured_at.year for entry in visible_entries_qs if entry.captured_at)
    ]

    context = {
        "page_title": "喜欢的景色",
        "entries": entries,
        "selected_entry": selected_entry,
        "selected_photos": list(selected_entry.photos.all()) if selected_entry else [],
        "active_filters": {
            "q": q,
            "city": city,
            "year": year,
        },
        "location_filters": location_filters,
        "year_filters": year_filters,
        "editor_mode": editor_mode,
        "form": form,
        "can_edit": can_edit,
        "filter_query": _build_query_string(q=q, city=city, year=year),
    }
    return render(request, "scenery/index.html", context)


def _build_query_string(**params):
    cleaned = {key: value for key, value in params.items() if value}
    if not cleaned:
        return ""
    return f"?{urlencode(cleaned)}"


def _user_can_edit(user):
    return getattr(user, "is_authenticated", False) and (
        getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
    )


def _require_editor(request):
    if not request.user.is_authenticated:
        login_url = reverse("login")
        next_param = urlencode({"next": request.get_full_path()})
        return redirect(f"{login_url}?{next_param}")
    if not _user_can_edit(request.user):
        return HttpResponseForbidden("当前账号没有编辑权限。")
    return None

