from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from apps.books.models import Book
from apps.core.site_data import SITE_TAGLINE, get_site_modules


def index(request):
    modules = get_site_modules()
    visible_books = list(Book.objects.visible_to_user(request.user))
    latest_book = visible_books[0] if visible_books else None
    implemented_modules = sum(1 for module in modules if module["available"])
    today = timezone.localdate()

    hero = {
        "eyebrow": f"{today:%Y年%m月%d日} / {SITE_TAGLINE}",
        "title": "我把真正留下来的东西，放在这里，让它们缓慢流过。",
        "body": (
            "这里不是展示型官网，而是一份仍在生长的个人档案册入口。"
            " 书、声音、食物和风景不急着解释自己，只先在首页安静出现。"
        ),
        "primary_action": {"label": "进入私人藏书室", "path": reverse("books:index")},
        "secondary_action": {"label": "看记忆溪流", "path": "/#memory-streams"},
    }

    memory_streams = _build_memory_streams(visible_books)

    recent_updates = [
        {
            "module": "收藏书籍",
            "summary": f"最近整理到《{latest_book.title}》。"
            if latest_book
            else "书影流已经接上真实封面，后续会继续把更多模块流入首页。",
            "time": latest_book.updated_at.strftime("%Y-%m-%d")
            if latest_book
            else "第一版",
            "path": reverse("books:detail", args=[latest_book.pk])
            if latest_book
            else reverse("books:index"),
        },
        {
            "module": "首页",
            "summary": "首页开始承担“记忆溪流”角色，让内容以流带而不是卡片墙的方式出现。",
            "time": "施工中",
            "path": "/#memory-streams",
        },
        {
            "module": "喜欢的美食",
            "summary": "食味流已预留位置，等真实内容录入后会直接接入首页流带。",
            "time": "待录入",
            "path": reverse("core:food"),
        },
        {
            "module": "喜欢的音乐",
            "summary": "声纹流结构已就位，后续会改为真实专辑封面与播放相关信息。",
            "time": "待录入",
            "path": reverse("core:music"),
        },
    ]

    context = {
        "page_title": "首页",
        "hero": hero,
        "memory_streams": memory_streams,
        "modules": modules,
        "recent_updates": recent_updates,
        "archive_quote": "流过首页的，只是入口。真正的停留，发生在每一个板块里面。",
        "module_index_summary": (
            f"{implemented_modules} 个板块已经进入首版建设，其余入口保持独立，"
            "以后新增页面时不需要推翻首页，只需要把新的流向接进来。"
        ),
    }
    return render(request, "home/index.html", context)


def _build_memory_streams(books):
    book_items = [_build_book_stream_item(book) for book in books]
    return [
        {
            "key": "books",
            "tone": "books",
            "title": "书影流",
            "subtitle": "私人藏书",
            "description": "读过的、在读的、准备靠近的，都先以封面留下。",
            "count_label": f"{len(book_items)} 本" if book_items else "尚未入册",
            "enter_label": "进入藏书室",
            "path": reverse("books:index"),
            "rows": _build_stream_rows(
                book_items,
                lane_count=2,
                direction="left",
                durations=(78, 92),
            ),
            "empty_note": None if book_items else "第一本书录入后，书影流会从这里开始缓慢流动。",
        },
        {
            "key": "music",
            "tone": "music",
            "title": "声纹流",
            "subtitle": "喜欢的音乐",
            "description": "一首歌有时比一句话更像记忆本身。",
            "count_label": "待录入",
            "enter_label": "进入音乐页",
            "path": reverse("core:music"),
            "rows": _build_placeholder_rows(
                kind="music",
                lane_count=1,
                direction="right",
                durations=(52,),
                item_count=12,
            ),
            "empty_note": "真实音乐内容录入后，会在这里以专辑封面的方式持续流过。",
        },
        {
            "key": "food",
            "tone": "food",
            "title": "食味流",
            "subtitle": "喜欢的美食",
            "description": "我记住的不只是味道，还有它靠近生活的方式。",
            "count_label": "待录入",
            "enter_label": "进入美食页",
            "path": reverse("core:food"),
            "rows": _build_placeholder_rows(
                kind="food",
                lane_count=2,
                direction="left",
                durations=(66, 58),
                item_count=8,
            ),
            "empty_note": "食物照片和做法录入后，会把这条流带从占位变成真实生活切片。",
        },
        {
            "key": "scenery",
            "tone": "scenery",
            "title": "风景流",
            "subtitle": "喜欢的景色",
            "description": "有些地方并不属于我，却长期停在我的视线里。",
            "count_label": "待录入",
            "enter_label": "进入景色页",
            "path": reverse("core:scenery"),
            "rows": _build_placeholder_rows(
                kind="scenery",
                lane_count=1,
                direction="right",
                durations=(74,),
                item_count=7,
            ),
            "empty_note": "景色模块有真实照片后，这里会变成横向漂流的远景带。",
        },
    ]


def _build_book_stream_item(book):
    return {
        "id": f"book-{book.pk}",
        "kind": "book",
        "title": book.title,
        "meta": book.get_status_display(),
        "path": reverse("books:detail", args=[book.pk]),
        "image_url": book.cover_image_url,
        "fallback": (book.title or "?")[:1],
    }


def _build_stream_rows(items, lane_count, direction, durations):
    if not items:
        return []

    rows = []
    for index in range(lane_count):
        lane_items = items[index::lane_count] or items
        lane_items = _ensure_lane_density(lane_items, minimum_items=6)
        rows.append(
            {
                "direction": direction,
                "duration": durations[index % len(durations)],
                "items": lane_items + lane_items,
            }
        )
    return rows


def _build_placeholder_rows(kind, lane_count, direction, durations, item_count):
    placeholders = [
        {
            "id": f"{kind}-ghost-{index}",
            "kind": kind,
            "placeholder": True,
        }
        for index in range(item_count)
    ]
    rows = _build_stream_rows(placeholders, lane_count, direction, durations)
    for row in rows:
        for item in row["items"]:
            item["placeholder"] = True
    return rows


def _ensure_lane_density(items, minimum_items):
    if not items:
        return []
    lane_items = list(items)
    while len(lane_items) < minimum_items:
        lane_items.extend(items)
    return lane_items[: max(minimum_items, len(items))]
