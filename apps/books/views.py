from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.books.forms import BookEditorForm
from apps.books.models import Book, BookAsset, BookTag


def index(request):
    return _render_books_page(request)


def detail(request, book_id):
    return _render_books_page(request, selected_id=book_id)


def create_book(request):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    if request.method != "POST":
        return redirect(f"{reverse('books:index')}?editor=create")

    form = BookEditorForm(request.POST, request.FILES)
    if form.is_valid():
        uploaded_asset = form.cleaned_data.get("asset_file")
        book = form.save()
        if uploaded_asset:
            messages.success(request, f"已加入《{book.title}》，并上传文件《{uploaded_asset.name}》。")
        else:
            messages.success(request, f"已加入《{book.title}》。")
        return redirect("books:detail", book_id=book.pk)

    return _render_books_page(request, form=form, editor_mode="create")


def edit_book(request, book_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    book = get_object_or_404(Book, pk=book_id)
    if request.method != "POST":
        return redirect(f"{reverse('books:detail', kwargs={'book_id': book.pk})}?editor=edit")

    form = BookEditorForm(request.POST, request.FILES, instance=book)
    if form.is_valid():
        uploaded_asset = form.cleaned_data.get("asset_file")
        book = form.save()
        if uploaded_asset:
            messages.success(request, f"《{book.title}》已更新，并附加文件《{uploaded_asset.name}》。")
        else:
            messages.success(request, f"《{book.title}》已更新。")
        return redirect("books:detail", book_id=book.pk)

    return _render_books_page(request, selected_id=book.pk, form=form, editor_mode="edit")


def delete_book(request, book_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    book = get_object_or_404(Book, pk=book_id)
    if request.method == "POST":
        title = book.title
        book.delete()
        messages.success(request, f"已删除《{title}》。")
    return redirect("books:index")


@login_required
def download_asset(request, asset_id):
    asset = get_object_or_404(BookAsset.objects.select_related("book"), pk=asset_id)
    if (
        not asset.download_enabled
        or not asset.book.is_visible_to(request.user)
        or not asset.can_access(request.user)
    ):
        return HttpResponseForbidden("当前账号无法下载该文件。")

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

    asset = get_object_or_404(BookAsset.objects.select_related("book"), pk=asset_id)
    book_id = asset.book_id
    if request.method == "POST":
        asset.file.delete(save=False)
        asset.delete()
        messages.success(request, "文件已删除。")
    return redirect("books:detail", book_id=book_id)


def _render_books_page(request, selected_id=None, form=None, editor_mode=None):
    visible_books_qs = Book.objects.visible_to_user(request.user)
    books_qs = visible_books_qs
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    tag = request.GET.get("tag", "").strip()

    if q:
        books_qs = books_qs.filter(
            Q(title__icontains=q)
            | Q(subtitle__icontains=q)
            | Q(author__icontains=q)
            | Q(publisher__icontains=q)
            | Q(tag_links__name__icontains=q)
            | Q(short_review__icontains=q)
            | Q(why_it_matters__icontains=q)
            | Q(long_note__icontains=q)
        )
    if status and status in {choice[0] for choice in Book.Status.choices}:
        books_qs = books_qs.filter(status=status)
    if tag:
        books_qs = books_qs.filter(tag_links__name=tag)

    books = list(books_qs.distinct().prefetch_related("assets", "tag_links"))
    selected_book = None
    if selected_id is not None:
        selected_book = next((book for book in books if book.pk == selected_id), None)
        if selected_book is None:
            raise Http404("Book not found")
    elif books:
        selected_book = books[0]

    can_edit = _user_can_edit(request.user)
    if editor_mode is None:
        editor_mode = request.GET.get("editor")
    if not can_edit:
        editor_mode = None
    if editor_mode == "edit" and selected_book is None:
        editor_mode = None

    if form is None:
        if editor_mode == "edit" and selected_book is not None:
            form = BookEditorForm(instance=selected_book)
        elif editor_mode == "create":
            form = BookEditorForm()

    available_tags = list(
        BookTag.objects.filter(books__in=visible_books_qs).distinct().order_by("name")
    )
    asset_rows = []
    if selected_book is not None:
        for asset in selected_book.assets.all():
            if asset.visibility == BookAsset.Visibility.PRIVATE and not can_edit:
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
        "page_title": "收藏书籍",
        "books": books,
        "selected_book": selected_book,
        "asset_rows": asset_rows,
        "status_filters": Book.Status.choices,
        "available_tags": available_tags,
        "active_filters": {
            "q": q,
            "status": status,
            "tag": tag,
        },
        "editor_mode": editor_mode,
        "form": form,
        "can_edit": can_edit,
        "filter_query": _build_query_string(q=q, status=status, tag=tag),
    }
    return render(request, "books/index.html", context)


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
