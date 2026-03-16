import json
import re
from dataclasses import dataclass
from html import unescape
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.core import signing

from apps.books.models import Book


REQUEST_TIMEOUT = 8
PREVIEW_TOKEN_SALT = "books.metadata.preview"
PREVIEW_TOKEN_MAX_AGE = 600

PROVIDER_LABELS = {
    "weread": "微信读书",
    "douban": "豆瓣",
    "openlibrary": "Open Library",
}

ENRICHABLE_FIELDS = (
    "cover_image_url",
    "author",
    "translator",
    "publisher",
    "subtitle",
    "short_review",
)

FIELD_LABELS = {
    field_name: str(Book._meta.get_field(field_name).verbose_name)
    for field_name in ENRICHABLE_FIELDS
}


class MetadataError(Exception):
    pass


class MetadataProviderUnavailable(MetadataError):
    pass


@dataclass
class MetadataCandidate:
    source_id: str
    title: str = ""
    subtitle: str = ""
    author: str = ""
    translator: str = ""
    publisher: str = ""
    cover_image_url: str = ""
    intro: str = ""
    short_review: str = ""

    def as_form_values(self):
        return {
            "cover_image_url": self.cover_image_url.strip(),
            "author": self.author.strip(),
            "translator": self.translator.strip(),
            "publisher": self.publisher.strip(),
            "subtitle": self.subtitle.strip(),
            "short_review": self.short_review.strip(),
        }

    def to_payload(self):
        return {
            "sourceId": self.source_id,
            "title": self.title,
            "subtitle": self.subtitle,
            "author": self.author,
            "translator": self.translator,
            "publisher": self.publisher,
            "coverImageUrl": self.cover_image_url,
            "intro": self.intro,
            "shortReview": self.short_review,
        }


def get_metadata_provider_options():
    return [
        {"id": provider_id, "label": label}
        for provider_id, label in PROVIDER_LABELS.items()
    ]


def get_metadata_batch_field_options():
    return [
        {"id": field_name, "label": FIELD_LABELS[field_name]}
        for field_name in ENRICHABLE_FIELDS
    ]


def build_metadata_preview(book, provider_id, query=""):
    provider_label = PROVIDER_LABELS.get(provider_id)
    if provider_label is None:
        raise ValueError("unsupported provider")

    resolved_query = (query or "").strip() or book.title

    try:
        candidate = _lookup_candidate(provider_id, resolved_query, book)
    except MetadataProviderUnavailable:
        return {
            "success": True,
            "status": "unavailable",
            "provider": {"id": provider_id, "label": provider_label},
            "message": f"{provider_label} 当前暂时不可用，请稍后再试。",
        }

    if candidate is None:
        return {
            "success": True,
            "status": "not_found",
            "provider": {"id": provider_id, "label": provider_label},
            "message": f"未在{provider_label}找到匹配结果。",
        }

    incoming_values = candidate.as_form_values()
    field_diffs = _build_field_diffs(book, incoming_values)
    if not field_diffs:
        return {
            "success": True,
            "status": "no_changes",
            "provider": {"id": provider_id, "label": provider_label},
            "candidate": candidate.to_payload(),
            "message": "已找到书籍，但当前没有可补全的差异字段。",
        }

    preview_token = signing.dumps(
        {
            "book_id": book.pk,
            "provider": provider_id,
            "values": {
                field_name: incoming_values[field_name]
                for field_name in ENRICHABLE_FIELDS
                if incoming_values.get(field_name)
            },
            "candidate": candidate.to_payload(),
        },
        salt=PREVIEW_TOKEN_SALT,
        compress=True,
    )

    return {
        "success": True,
        "status": "found",
        "previewToken": preview_token,
        "provider": {"id": provider_id, "label": provider_label},
        "candidate": candidate.to_payload(),
        "fields": field_diffs,
    }


def apply_metadata_preview(book, preview_token, field_names):
    try:
        payload = signing.loads(
            preview_token,
            salt=PREVIEW_TOKEN_SALT,
            max_age=PREVIEW_TOKEN_MAX_AGE,
        )
    except signing.SignatureExpired as exc:
        raise ValueError("preview token expired") from exc
    except signing.BadSignature as exc:
        raise ValueError("preview token invalid") from exc

    if payload.get("book_id") != book.pk:
        raise ValueError("preview token mismatch")

    raw_values = payload.get("values") or {}
    selected_fields = []
    seen = set()
    for field_name in field_names or []:
        if field_name in seen or field_name not in ENRICHABLE_FIELDS:
            continue
        if not raw_values.get(field_name):
            continue
        seen.add(field_name)
        selected_fields.append(field_name)

    if not selected_fields:
        raise ValueError("no fields selected")

    values = {
        field_name: raw_values[field_name]
        for field_name in selected_fields
    }
    return {
        "success": True,
        "updatedFields": selected_fields,
        "values": values,
        "message": f"已将 {len(selected_fields)} 个字段填入当前表单，请继续点击保存。",
    }


def apply_bulk_metadata_field(books, provider_id, field_name):
    provider_label = PROVIDER_LABELS.get(provider_id)
    if provider_label is None:
        raise ValueError("unsupported provider")
    if field_name not in ENRICHABLE_FIELDS:
        raise ValueError("unsupported field")

    processed_books = list(books)
    summary = {
        "total": len(processed_books),
        "updated": 0,
        "unchanged": 0,
        "not_found": 0,
        "no_value": 0,
        "unavailable": 0,
    }
    results = []

    for book in processed_books:
        try:
            candidate = _lookup_candidate(provider_id, book.title, book)
        except MetadataProviderUnavailable:
            summary["unavailable"] += 1
            results.append(
                {
                    "bookId": book.pk,
                    "title": book.title,
                    "status": "unavailable",
                    "message": f"{provider_label} 当前暂时不可用。",
                }
            )
            continue

        if candidate is None:
            summary["not_found"] += 1
            results.append(
                {
                    "bookId": book.pk,
                    "title": book.title,
                    "status": "not_found",
                    "message": "没有找到匹配结果。",
                }
            )
            continue

        incoming_value = _normalize_text_value(candidate.as_form_values().get(field_name))
        current_value = _normalize_text_value(getattr(book, field_name, ""))

        if not incoming_value:
            summary["no_value"] += 1
            results.append(
                {
                    "bookId": book.pk,
                    "title": book.title,
                    "status": "no_value",
                    "message": "该来源没有返回这个字段的值。",
                }
            )
            continue

        if current_value == incoming_value:
            summary["unchanged"] += 1
            results.append(
                {
                    "bookId": book.pk,
                    "title": book.title,
                    "status": "unchanged",
                    "message": "当前值和外部结果一致，已跳过。",
                }
            )
            continue

        setattr(book, field_name, incoming_value)
        book.save(update_fields=[field_name, "updated_at"])
        summary["updated"] += 1
        results.append(
            {
                "bookId": book.pk,
                "title": book.title,
                "status": "updated",
                "message": "已更新。",
                "value": incoming_value,
            }
        )

    return {
        "success": True,
        "provider": {"id": provider_id, "label": provider_label},
        "field": {"id": field_name, "label": FIELD_LABELS[field_name]},
        "summary": summary,
        "results": results,
        "message": _build_bulk_update_message(summary),
    }


def _build_field_diffs(book, incoming_values):
    diffs = []
    for field_name in ENRICHABLE_FIELDS:
        incoming_value = _normalize_text_value(incoming_values.get(field_name))
        if not incoming_value:
            continue
        current_value = _normalize_text_value(getattr(book, field_name, ""))
        if current_value == incoming_value:
            continue
        diffs.append(
            {
                "name": field_name,
                "label": FIELD_LABELS[field_name],
                "current": current_value,
                "incoming": incoming_value,
                "changed": True,
                "defaultSelected": not bool(current_value),
            }
        )
    return diffs


def _lookup_candidate(provider_id, query, book):
    if provider_id == "weread":
        return _lookup_weread(query, book)
    if provider_id == "douban":
        return _lookup_douban(query, book)
    if provider_id == "openlibrary":
        return _lookup_openlibrary(query, book)
    raise ValueError("unsupported provider")


def _lookup_weread(query, book):
    payload = _fetch_json(
        f"https://weread.qq.com/web/search/global?keyword={quote(query)}"
    )
    rows = payload.get("books") or []
    if not rows:
        return None

    candidates = []
    for row in rows:
        book_info = row.get("bookInfo") or {}
        title = (book_info.get("title") or "").strip()
        if not title:
            continue
        intro = _clean_whitespace(book_info.get("intro") or "")
        candidates.append(
            MetadataCandidate(
                source_id=str(book_info.get("bookId") or ""),
                title=title,
                author=_clean_whitespace(book_info.get("author") or ""),
                translator=_clean_whitespace(book_info.get("translator") or ""),
                publisher=_clean_whitespace(book_info.get("publisher") or ""),
                cover_image_url=(book_info.get("cover") or "").strip(),
                intro=intro,
                short_review=_build_short_review(title, book_info.get("author") or "", intro),
            )
        )
    return _pick_best_candidate(candidates, query, book)


def _lookup_openlibrary(query, book):
    payload = _fetch_json(
        f"https://openlibrary.org/search.json?title={quote(query)}&limit=6"
    )
    rows = payload.get("docs") or []
    candidates = []
    for row in rows:
        title = _clean_whitespace(row.get("title") or "")
        if not title:
            continue
        cover_i = row.get("cover_i")
        cover_image_url = (
            f"https://covers.openlibrary.org/b/id/{cover_i}-L.jpg"
            if cover_i
            else ""
        )
        author_names = row.get("author_name") or []
        publisher_names = row.get("publisher") or []
        subtitle = _clean_whitespace(row.get("subtitle") or "")
        candidates.append(
            MetadataCandidate(
                source_id=str(row.get("key") or ""),
                title=title,
                subtitle=subtitle,
                author=_clean_whitespace(author_names[0] if author_names else ""),
                publisher=_clean_whitespace(publisher_names[0] if publisher_names else ""),
                cover_image_url=cover_image_url,
                short_review=_build_short_review(
                    title,
                    author_names[0] if author_names else "",
                    "",
                ),
            )
        )
    return _pick_best_candidate(candidates, query, book)


def _lookup_douban(query, book):
    html = _fetch_text(
        f"https://www.douban.com/search?cat=1001&q={quote(query)}"
    )
    matches = re.findall(
        (
            r'<div class="result">.*?<a class="nbg"[^>]*title="(?P<title>[^"]+)"[^>]*>'
            r"\s*<img src=\"(?P<cover>[^\"]+)\".*?"
            r"<span class=\"subject-cast\">(?P<cast>.*?)</span>"
            r".*?<p>(?P<intro>.*?)</p>"
        ),
        html,
        re.S,
    )
    if not matches:
        return None

    candidates = []
    for title, cover, subject_cast, intro in matches:
        parsed = _parse_douban_subject_cast(subject_cast)
        cleaned_title = _clean_html(title)
        cleaned_intro = _clean_html(intro)
        candidates.append(
            MetadataCandidate(
                source_id=_extract_douban_subject_id(html, cleaned_title, cover),
                title=cleaned_title,
                author=parsed["author"],
                translator=parsed["translator"],
                publisher=parsed["publisher"],
                cover_image_url=_clean_whitespace(cover),
                intro=cleaned_intro,
                short_review=_build_short_review(
                    cleaned_title,
                    parsed["author"],
                    cleaned_intro,
                ),
            )
        )
    return _pick_best_candidate(candidates, query, book)


def _extract_douban_subject_id(html, title, cover):
    pattern = re.compile(
        r'<div class="result">.*?title="%s".*?<img src="%s".*?sid:\s*(\d+)'
        % (re.escape(title), re.escape(cover)),
        re.S,
    )
    match = pattern.search(html)
    if match:
        return match.group(1)
    return ""


def _parse_douban_subject_cast(value):
    parts = [
        _clean_html(part)
        for part in value.split("/")
        if _clean_html(part)
    ]
    if not parts:
        return {"author": "", "translator": "", "publisher": ""}

    publisher = ""
    translator = ""
    author_parts = parts[:]

    if parts and re.fullmatch(r"\d{4}([-~]\d{4})?", parts[-1]):
        author_parts = parts[:-1]

    if len(author_parts) >= 2:
        publisher = author_parts[-1]
        author_parts = author_parts[:-1]

    if len(author_parts) >= 2:
        translator = author_parts[-1]
        author_parts = author_parts[:-1]

    author = " / ".join(author_parts).strip()
    return {
        "author": author,
        "translator": translator,
        "publisher": publisher,
    }


def _pick_best_candidate(candidates, query, book):
    if not candidates:
        return None

    best = max(
        candidates,
        key=lambda candidate: _candidate_score(candidate, query, book),
    )
    return best


def _candidate_score(candidate, query, book):
    score = 0
    target_title = _normalize_for_match(book.title or "")
    query_title = _normalize_for_match(query)
    candidate_title = _normalize_for_match(candidate.title)
    book_author = _normalize_for_match(book.author or "")
    candidate_author = _normalize_for_match(candidate.author)

    if target_title and candidate_title == target_title:
        score += 12
    if query_title and candidate_title == query_title:
        score += 8
    if target_title and target_title in candidate_title:
        score += 5
    if query_title and query_title and query_title in candidate_title:
        score += 4
    if book_author and candidate_author and book_author in candidate_author:
        score += 3
    if candidate.cover_image_url:
        score += 1
    if candidate.publisher:
        score += 1
    return score


def _build_short_review(title, author, intro):
    intro_text = _clean_whitespace(intro)
    if intro_text:
        first_sentence = re.split(r"[。！？.!?]", intro_text, maxsplit=1)[0].strip()
        if first_sentence:
            return _truncate_text(first_sentence, 72)
    summary_bits = [bit for bit in [title.strip(), author.strip()] if bit]
    if not summary_bits:
        return ""
    return _truncate_text("，".join(summary_bits), 72)


def _fetch_json(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise MetadataProviderUnavailable from exc


def _fetch_text(url):
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT) as response:
            return response.read().decode("utf-8", errors="ignore")
    except (HTTPError, URLError, TimeoutError) as exc:
        raise MetadataProviderUnavailable from exc


def _normalize_text_value(value):
    return _clean_whitespace(str(value or ""))


def _normalize_for_match(value):
    return re.sub(r"[\W_]+", "", _normalize_text_value(value).casefold())


def _clean_html(value):
    return _clean_whitespace(re.sub(r"<[^>]+>", "", unescape(value or "")))


def _clean_whitespace(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _truncate_text(value, limit):
    text = _clean_whitespace(value)
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rstrip()}…"


def _build_bulk_update_message(summary):
    if summary["updated"]:
        return f"批量更新完成，已更新 {summary['updated']} 本。"
    if summary["not_found"] == summary["total"] and summary["total"]:
        return "所选书籍都没有找到匹配结果。"
    if summary["unavailable"] == summary["total"] and summary["total"]:
        return "当前来源暂时不可用，请稍后再试。"
    return "批量更新已完成，没有可写入的新值。"
