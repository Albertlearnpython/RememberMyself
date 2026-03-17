from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from apps.books.models import Book
from apps.core.site_data import SITE_TAGLINE, get_site_modules
from apps.music.models import MusicTrack
from apps.scenery.models import SceneryEntry


HOME_PROFILE = {
    "name": "孙伯符",
    "handle": "Noah Brooks",
    "role": "Python / AI / 阅读",
    "location": "深圳",
    "organization": "华南农业大学 · 本科",
    "summary": "一个喜欢读书的人。",
    "hero_title": "孙伯符 / Noah Brooks",
    "hero_subtitle": "在深圳记录 Python、AI、阅读与持续搭建，把零散的学习过程整理成长期作品。",
    "motto": "静水流深，金石为开；守拙见慧，癸水逢源。",
    "avatar_asset": "site/avatar-wechat.jpg",
    "avatar_label": "孙",
    "contact_label": "微信",
    "contact_value": "djm13126042156",
    "tags": [
        "Python",
        "AI",
        "阅读",
        "深圳",
        "华南农业大学",
    ],
}

HOME_TIMELINE = [
    {"date": "2026-03-14", "title": "RememberMyself 项目启动"},
    {"date": "进行中", "title": "持续整理书籍、音乐与长期记录"},
    {"date": "下一步", "title": "把更多真实页面和个人内容接进首页"},
]


def index(request):
    modules = get_site_modules()
    visible_books = list(Book.objects.visible_to_user(request.user))
    visible_tracks = list(MusicTrack.objects.visible_to_user(request.user))
    visible_scenery = list(SceneryEntry.objects.visible_to_user(request.user).prefetch_related("photos"))
    latest_book = visible_books[0] if visible_books else None
    latest_track = visible_tracks[0] if visible_tracks else None
    latest_scenery = visible_scenery[0] if visible_scenery else None
    implemented_modules = sum(1 for module in modules if module["available"])
    today = timezone.localdate()

    hero = {
        "eyebrow": f"{today:%Y年%m月%d日} / {SITE_TAGLINE}",
        "title": "我把真正留下来的东西，放在这里，让它们缓慢流过。",
        "body": (
            "这里不是展示型官网，而是一份仍在生长的个人档案册入口。"
            " 书、声音、食物和风景不急着解释自己，只先在首页安静出现。"
        ),
        "primary_action": {"label": "进入藏书室", "path": reverse("books:index")},
        "secondary_action": {"label": "看记忆溪流", "path": "/#memory-streams"},
    }
    home_stats = [
        {
            "label": "已入藏书",
            "value": len(visible_books),
            "note": "把读过、正在读和想读的东西慢慢归档。",
        },
        {
            "label": "已归档音乐",
            "value": len(visible_tracks),
            "note": "封面与文件都能在这里留下来。",
        },
        {
            "label": "已落地板块",
            "value": implemented_modules,
            "note": "以后新增页面时，不需要推翻首页结构。",
        },
    ]

    memory_streams = _build_memory_streams(visible_books, visible_tracks, visible_scenery)

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
            "module": "喜欢的景色",
            "summary": f"最近收进“{latest_scenery.display_title}”。"
            if latest_scenery
            else "风景流已经接好上传和自动识别结构，等第一批真实照片流入首页。",
            "time": latest_scenery.updated_at.strftime("%Y-%m-%d")
            if latest_scenery
            else "第一版",
            "path": reverse("scenery:detail", args=[latest_scenery.pk])
            if latest_scenery
            else reverse("scenery:index"),
        },
        {
            "module": "喜欢的音乐",
            "summary": f"最近加入《{latest_track.title}》。"
            if latest_track
            else "声纹流结构已就位，等第一批真实音乐入库后会直接接入首页。",
            "time": latest_track.updated_at.strftime("%Y-%m-%d")
            if latest_track
            else "第一版",
            "path": reverse("music:detail", args=[latest_track.pk])
            if latest_track
            else reverse("music:index"),
        },
    ]

    context = {
        "page_title": "首页",
        "hero": hero,
        "profile": HOME_PROFILE,
        "profile_timeline": HOME_TIMELINE,
        "home_stats": home_stats,
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


def _build_memory_streams(books, tracks, scenery_entries):
    book_items = [_build_book_stream_item(book) for book in books]
    music_items = [_build_music_stream_item(track) for track in tracks]
    scenery_items = _build_scenery_stream_items(scenery_entries)
    return [
        {
            "key": "books",
            "tone": "books",
            "title": "书影流",
            "subtitle": "藏书归档",
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
            "count_label": f"{len(music_items)} 首" if music_items else "尚未入库",
            "enter_label": "进入音乐页",
            "path": reverse("music:index"),
            "rows": _build_stream_rows(
                music_items,
                lane_count=1,
                direction="right",
                durations=(52,),
            )
            if music_items
            else _build_placeholder_rows(
                kind="music",
                lane_count=1,
                direction="right",
                durations=(52,),
                item_count=12,
            ),
            "empty_note": None if music_items else "第一首音乐录入后，声纹流会开始带着真实封面缓慢流过。",
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
            "subtitle": "景色归档",
            "description": "手机拍下的那一刻，会把时间、地点和心情一起留下来。",
            "count_label": f"{len(scenery_items)} 张" if scenery_items else "尚未入册",
            "enter_label": "进入景色页",
            "path": reverse("scenery:index"),
            "rows": _build_stream_rows(
                scenery_items,
                lane_count=1,
                direction="right",
                durations=(74,),
            )
            if scenery_items
            else _build_placeholder_rows(
                kind="scenery",
                lane_count=1,
                direction="right",
                durations=(74,),
                item_count=7,
            ),
            "empty_note": None if scenery_items else "第一组景色录入后，风景流会从这里开始缓慢漂过首页。",
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


def _build_music_stream_item(track):
    return {
        "id": f"music-{track.pk}",
        "kind": "music",
        "title": track.title,
        "meta": track.artist or track.album or "已归档",
        "path": reverse("music:detail", args=[track.pk]),
        "image_url": track.cover_image_url,
        "fallback": (track.title or "?")[:1],
    }


def _build_scenery_stream_items(entries):
    items = []
    for entry in entries:
        cached_photos = getattr(entry, "_prefetched_objects_cache", {}).get("photos")
        photos = list(cached_photos if cached_photos is not None else entry.photos.all())
        if not photos:
            continue

        total = len(photos)
        for index, photo in enumerate(photos, start=1):
            meta_parts = []
            if total > 1:
                meta_parts.append(f"{index}/{total}")
            location = entry.location_summary
            if location:
                meta_parts.append(location)
            captured_at = photo.taken_at or entry.captured_at
            if captured_at:
                meta_parts.append(f"{timezone.localtime(captured_at):%Y-%m-%d}")

            items.append(
                {
                    "id": f"scenery-{entry.pk}-{photo.pk}",
                    "kind": "scenery",
                    "title": entry.display_title,
                    "meta": " · ".join(meta_parts) if meta_parts else "景色照片",
                    "path": reverse("scenery:detail", args=[entry.pk]),
                    "image_url": photo.image_url,
                    "fallback": (entry.display_title or "?")[:1],
                }
            )
    return items


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
