from django.shortcuts import render
from django.utils import timezone

from apps.books.models import Book
from apps.core.site_data import SITE_TAGLINE, get_site_modules


def index(request):
    modules = get_site_modules()
    visible_books = Book.objects.visible_to_user(request.user)
    current_book = visible_books.filter(
        status__in=[Book.Status.READING, Book.Status.REVISITING]
    ).first() or visible_books.first()
    latest_book = visible_books.first()
    total_books = visible_books.count()
    implemented_modules = sum(1 for module in modules if module["available"])
    today = timezone.localdate()

    hero = {
        "eyebrow": f"{today:%Y年%m月%d日} · {SITE_TAGLINE}",
        "title": "记住自己，是一场缓慢而长期的整理。",
        "body": (
            "这里不是展示型官网，而是一份会持续扩展的个人档案册入口。"
            "首页只做一件事：安静、精确地把重要的东西带到你眼前。"
        ),
        "primary_action": {"label": "进入收藏书籍", "path": "/books/"},
        "secondary_action": {"label": "查看当前关注", "path": "/#current-focus"},
    }

    focus_items = [
        {
            "eyebrow": "当前阅读",
            "title": current_book.title if current_book else "还没有放入第一本书",
            "meta": current_book.author if current_book and current_book.author else "从书籍页开始建立你的第一份私人阅览室。",
            "path": "/books/",
        },
        {
            "eyebrow": "书籍馆藏",
            "title": f"{total_books} 本已归入目录" if total_books else "目录仍在建立中",
            "meta": "公开阅读，登录后可进入受保护资源与编辑流程。",
            "path": "/books/",
        },
        {
            "eyebrow": "模块进度",
            "title": f"{implemented_modules} / {len(modules)} 个板块进入首版开发",
            "meta": "首页与收藏书籍已开工，其余板块保留独立入口和后续扩展空间。",
            "path": "/#module-index",
        },
        {
            "eyebrow": "记录方式",
            "title": "每个板块独立，但共用同一套安静秩序",
            "meta": "以后新增页面时，不需要推翻整体结构，只是在总索引里增加一页。",
            "path": "/methods/",
        },
    ]

    recent_updates = [
        {
            "module": "收藏书籍",
            "summary": f"最近整理到《{latest_book.title}》。"
            if latest_book
            else "首版书籍页已接上列表、详情、受保护文件与登录编辑入口。",
            "time": latest_book.updated_at.strftime("%Y-%m-%d")
            if latest_book
            else "第一版",
            "path": f"/books/{latest_book.pk}/" if latest_book else "/books/",
        },
        {
            "module": "首页",
            "summary": "首页开始承担总索引角色，提供模块面板、当前关注与最近更新。",
            "time": "第一版",
            "path": "/",
        },
        {
            "module": "喜欢的美食",
            "summary": "保留独立入口，后续会接上图片、做法与偏好记录。",
            "time": "设计阶段",
            "path": "/food/",
        },
        {
            "module": "喜欢的音乐",
            "summary": "后续会扩展上传、下载和播放能力，资源仍然纳入权限分层。",
            "time": "设计阶段",
            "path": "/music/",
        },
    ]

    context = {
        "page_title": "首页",
        "hero": hero,
        "focus_items": focus_items,
        "modules": modules,
        "recent_updates": recent_updates,
        "archive_quote": "这里不是信息流，而是慢慢长成的个人归档。",
    }
    return render(request, "home/index.html", context)
