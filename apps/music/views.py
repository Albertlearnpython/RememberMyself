from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.music.forms import MusicEditorForm
from apps.music.models import MusicAsset, MusicTag, MusicTrack


def index(request):
    return _render_music_page(request)


def detail(request, track_id):
    return _render_music_page(request, selected_id=track_id)


def create_track(request):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    if request.method != "POST":
        return redirect(f"{reverse('music:index')}?editor=create")

    form = MusicEditorForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_asset = form.cleaned_data.get("asset_file")
        track = form.save()
        if uploaded_asset:
            messages.success(request, f"已加入《{track.title}》，并上传音乐文件《{uploaded_asset.name}》。")
        else:
            messages.success(request, f"已加入《{track.title}》。")
        return redirect("music:detail", track_id=track.pk)

    return _render_music_page(request, form=form, editor_mode="create")


def edit_track(request, track_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    track = get_object_or_404(MusicTrack, pk=track_id)
    if request.method != "POST":
        return redirect(f"{reverse('music:detail', kwargs={'track_id': track.pk})}?editor=edit")

    form = MusicEditorForm(request.POST, request.FILES, instance=track)
    if form.is_valid():
        uploaded_asset = form.cleaned_data.get("asset_file")
        track = form.save()
        if uploaded_asset:
            messages.success(request, f"《{track.title}》已更新，并附加音乐文件《{uploaded_asset.name}》。")
        else:
            messages.success(request, f"《{track.title}》已更新。")
        return redirect("music:detail", track_id=track.pk)

    return _render_music_page(request, selected_id=track.pk, form=form, editor_mode="edit")


def delete_track(request, track_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    track = get_object_or_404(MusicTrack, pk=track_id)
    if request.method == "POST":
        title = track.title
        track.delete()
        messages.success(request, f"已删除《{title}》。")
    return redirect("music:index")


@login_required
def download_asset(request, asset_id):
    asset = get_object_or_404(MusicAsset.objects.select_related("track"), pk=asset_id)
    if (
        not asset.download_enabled
        or not asset.track.is_visible_to(request.user)
        or not asset.can_access(request.user)
    ):
        return HttpResponseForbidden("当前账号无法下载该音乐文件。")

    return FileResponse(
        asset.file.open("rb"),
        content_type=asset.mime_type,
        as_attachment=True,
        filename=asset.file_name,
    )


def delete_asset(request, asset_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    asset = get_object_or_404(MusicAsset.objects.select_related("track"), pk=asset_id)
    track_id = asset.track_id
    if request.method == "POST":
        asset.file.delete(save=False)
        asset.delete()
        messages.success(request, "音乐文件已删除。")
    return redirect("music:detail", track_id=track_id)


def _render_music_page(request, selected_id=None, form=None, editor_mode=None):
    visible_tracks_qs = MusicTrack.objects.visible_to_user(request.user)
    tracks_qs = visible_tracks_qs
    q = request.GET.get("q", "").strip()
    tag = request.GET.get("tag", "").strip()
    visibility = request.GET.get("visibility", "").strip()

    if q:
        tracks_qs = tracks_qs.filter(
            Q(title__icontains=q)
            | Q(artist__icontains=q)
            | Q(album__icontains=q)
            | Q(tag_links__name__icontains=q)
            | Q(short_review__icontains=q)
            | Q(why_it_matters__icontains=q)
            | Q(long_note__icontains=q)
        )
    if tag:
        tracks_qs = tracks_qs.filter(tag_links__name=tag)

    can_edit = _user_can_edit(request.user)
    if visibility and visibility in {choice[0] for choice in MusicTrack.Visibility.choices} and can_edit:
        tracks_qs = tracks_qs.filter(visibility=visibility)

    tracks = list(tracks_qs.distinct().prefetch_related("assets", "tag_links"))
    selected_track = None
    if selected_id is not None:
        selected_track = next((track for track in tracks if track.pk == selected_id), None)
        if selected_track is None:
            raise Http404("Track not found")
    elif tracks:
        selected_track = tracks[0]

    if editor_mode is None:
        editor_mode = request.GET.get("editor")
    if not can_edit:
        editor_mode = None
    if editor_mode == "edit" and selected_track is None:
        editor_mode = None

    if form is None:
        if editor_mode == "edit" and selected_track is not None:
            form = MusicEditorForm(instance=selected_track)
        elif editor_mode == "create":
            form = MusicEditorForm()

    available_tags = list(
        MusicTag.objects.filter(tracks__in=visible_tracks_qs).distinct().order_by("name")
    )
    asset_rows = []
    if selected_track is not None:
        for asset in selected_track.assets.all():
            if asset.visibility == MusicAsset.Visibility.PRIVATE and not can_edit:
                continue
            asset_rows.append(
                {
                    "asset": asset,
                    "can_download": request.user.is_authenticated
                    and asset.download_enabled
                    and asset.can_access(request.user),
                }
            )

    context = {
        "page_title": "喜欢的音乐",
        "tracks": tracks,
        "selected_track": selected_track,
        "asset_rows": asset_rows,
        "available_tags": available_tags,
        "active_filters": {
            "q": q,
            "tag": tag,
            "visibility": visibility,
        },
        "visibility_filters": MusicTrack.Visibility.choices,
        "editor_mode": editor_mode,
        "form": form,
        "can_edit": can_edit,
        "filter_query": _build_query_string(
            q=q,
            tag=tag,
            visibility=visibility if can_edit else "",
        ),
    }
    return render(request, "music/index.html", context)


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
