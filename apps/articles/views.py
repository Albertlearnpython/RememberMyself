from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.articles.forms import ArticleEditorForm
from apps.articles.models import ArticleEntry


def index(request):
    return _render_articles_page(request)


def detail(request, article_id):
    return _render_articles_page(request, selected_id=article_id)


def create_article(request):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    if request.method != "POST":
        return redirect(f"{reverse('articles:index')}?editor=create")

    form = ArticleEditorForm(request.POST, request.FILES)
    if form.is_valid():
        article = form.save()
        messages.success(request, f"已加入《{article.title}》。")
        return redirect("articles:detail", article_id=article.pk)

    return _render_articles_page(request, form=form, editor_mode="create")


def edit_article(request, article_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    article = get_object_or_404(ArticleEntry, pk=article_id)
    if request.method != "POST":
        return redirect(f"{reverse('articles:detail', kwargs={'article_id': article.pk})}?editor=edit")

    form = ArticleEditorForm(request.POST, request.FILES, instance=article)
    if form.is_valid():
        article = form.save()
        messages.success(request, f"《{article.title}》已更新，Markdown 源文件已同步覆盖。")
        return redirect("articles:detail", article_id=article.pk)

    return _render_articles_page(request, selected_id=article.pk, form=form, editor_mode="edit")


def delete_article(request, article_id):
    permission_response = _require_editor(request)
    if permission_response:
        return permission_response

    article = get_object_or_404(ArticleEntry, pk=article_id)
    if request.method == "POST":
        title = article.title
        if article.source_file:
            article.source_file.delete(save=False)
        article.delete()
        messages.success(request, f"已删除《{title}》。")
    return redirect("articles:index")


def download_source(request, article_id):
    article = get_object_or_404(ArticleEntry, pk=article_id)
    if not article.is_visible_to(request.user):
        raise Http404("Article not found")
    article.ensure_source_file()

    return FileResponse(
        article.source_file.open("rb"),
        content_type="text/markdown; charset=utf-8",
        as_attachment=True,
        filename=article.download_name,
    )


def _render_articles_page(request, selected_id=None, form=None, editor_mode=None):
    visible_articles_qs = ArticleEntry.objects.visible_to_user(request.user)
    articles_qs = visible_articles_qs
    q = request.GET.get("q", "").strip()
    visibility = request.GET.get("visibility", "").strip()

    if q:
        articles_qs = articles_qs.filter(
            Q(title__icontains=q)
            | Q(summary__icontains=q)
            | Q(markdown_content__icontains=q)
            | Q(source_filename__icontains=q)
        )

    can_edit = _user_can_edit(request.user)
    if visibility and visibility in {choice[0] for choice in ArticleEntry.Visibility.choices} and can_edit:
        articles_qs = articles_qs.filter(visibility=visibility)

    articles = list(articles_qs)
    selected_article = None
    if selected_id is not None:
        selected_article = next((article for article in articles if article.pk == selected_id), None)
        if selected_article is None:
            raise Http404("Article not found")
    elif articles:
        selected_article = articles[0]

    if editor_mode is None:
        editor_mode = request.GET.get("editor")
    if not can_edit:
        editor_mode = None
    if editor_mode == "edit" and selected_article is None:
        editor_mode = None

    if form is None:
        if editor_mode == "edit" and selected_article is not None:
            form = ArticleEditorForm(instance=selected_article)
        elif editor_mode == "create":
            form = ArticleEditorForm()

    context = {
        "page_title": "文章",
        "articles": articles,
        "selected_article": selected_article,
        "active_filters": {
            "q": q,
            "visibility": visibility,
        },
        "visibility_filters": ArticleEntry.Visibility.choices,
        "editor_mode": editor_mode,
        "form": form,
        "can_edit": can_edit,
        "filter_query": _build_query_string(
            q=q,
            visibility=visibility if can_edit else "",
        ),
    }
    return render(request, "articles/index.html", context)


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
