import json
import shutil
import tempfile
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.books.metadata import MetadataCandidate, _lookup_douban
from apps.books.models import Book, BookAsset, BookTag


User = get_user_model()


class BooksVisibilityTests(TestCase):
    def setUp(self):
        self.public_book = Book.objects.create(
            title="公开书籍",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )
        self.login_book = Book.objects.create(
            title="登录可见书籍",
            status=Book.Status.PLANNED,
            visibility=Book.Visibility.LOGIN_REQUIRED,
        )
        self.private_book = Book.objects.create(
            title="私密书籍",
            status=Book.Status.FINISHED,
            visibility=Book.Visibility.PRIVATE,
        )
        self.user = User.objects.create_user(username="viewer", password="pass123456")
        self.staff = User.objects.create_user(
            username="editor",
            password="pass123456",
            is_staff=True,
        )

    def test_guest_only_sees_public_books(self):
        response = self.client.get(reverse("books:index"))

        self.assertContains(response, "公开书籍")
        self.assertNotContains(response, "登录可见书籍")
        self.assertNotContains(response, "私密书籍")

    def test_authenticated_user_sees_login_required_books(self):
        self.client.login(username="viewer", password="pass123456")

        response = self.client.get(reverse("books:index"))

        self.assertContains(response, "公开书籍")
        self.assertContains(response, "登录可见书籍")
        self.assertNotContains(response, "私密书籍")

    def test_staff_user_sees_private_books_and_editor_entry(self):
        self.client.login(username="editor", password="pass123456")

        response = self.client.get(reverse("books:index"))

        self.assertContains(response, "私密书籍")
        self.assertContains(response, "新增书籍")


class BookAssetTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

        self.staff = User.objects.create_user(
            username="asset_admin",
            password="pass123456",
            is_staff=True,
        )
        self.book = Book.objects.create(
            title="资料归档测试书",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )
        self.shared_tag = BookTag.objects.create(name="养生")

    def test_create_book_with_upload_creates_asset_and_shared_tags(self):
        self.client.login(username="asset_admin", password="pass123456")

        response = self.client.post(
            reverse("books:create"),
            data={
                "title": "上传测试书",
                "subtitle": "",
                "author": "",
                "translator": "",
                "publisher": "",
                "publish_year": "",
                "cover_image_url": "",
                "status": Book.Status.PLANNED,
                "rating": "88",
                "word_count": "12.5",
                "tag_links": [self.shared_tag.pk],
                "new_tags": "内经, 养生",
                "short_review": "",
                "why_it_matters": "",
                "long_note": "",
                "reading_started_at": "",
                "reading_finished_at": "",
                "visibility": Book.Visibility.PUBLIC,
                "asset_type": BookAsset.AssetType.EBOOK,
                "asset_visibility": BookAsset.Visibility.LOGIN_REQUIRED,
                "download_enabled": "on",
                "asset_file": SimpleUploadedFile(
                    "sample.epub",
                    b"fake epub bytes",
                    content_type="application/epub+zip",
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(BookAsset.objects.count(), 1)
        self.assertEqual(BookAsset.objects.first().file_extension, ".epub")
        book = Book.objects.get(title="上传测试书")
        self.assertEqual(book.rating, 88)
        self.assertEqual(book.word_count, Decimal("12.50"))
        self.assertCountEqual(book.tag_list, ["养生", "内经"])
        self.assertEqual(BookTag.objects.filter(name="养生").count(), 1)
        self.assertEqual(BookTag.objects.count(), 2)

    def test_books_page_can_filter_by_shared_tag(self):
        tagged_book = Book.objects.create(
            title="养生书",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )
        tagged_book.tag_links.add(self.shared_tag)
        Book.objects.create(
            title="未打标签的书",
            status=Book.Status.PLANNED,
            visibility=Book.Visibility.PUBLIC,
        )

        response = self.client.get(reverse("books:index"), {"tag": "养生"})

        self.assertContains(response, "养生书")
        self.assertNotContains(response, "未打标签的书")

    def test_hundred_point_rating_rejects_out_of_range_value(self):
        self.client.login(username="asset_admin", password="pass123456")

        response = self.client.post(
            reverse("books:create"),
            data={
                "title": "评分超限测试",
                "subtitle": "",
                "author": "",
                "translator": "",
                "publisher": "",
                "publish_year": "",
                "cover_image_url": "",
                "status": Book.Status.PLANNED,
                "rating": "101",
                "short_review": "",
                "why_it_matters": "",
                "long_note": "",
                "reading_started_at": "",
                "reading_finished_at": "",
                "visibility": Book.Visibility.PUBLIC,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "小于或等于100")
        self.assertFalse(Book.objects.filter(title="评分超限测试").exists())

    def test_status_choices_no_longer_include_paused(self):
        self.assertNotIn("paused", dict(Book.Status.choices))

    def test_detail_page_only_shows_download_action_for_asset(self):
        self.client.login(username="asset_admin", password="pass123456")
        asset = BookAsset.objects.create(
            book=self.book,
            asset_type=BookAsset.AssetType.EBOOK,
            visibility=BookAsset.Visibility.LOGIN_REQUIRED,
            download_enabled=True,
            file=SimpleUploadedFile(
                "archive.epub",
                b"fake epub bytes",
                content_type="application/epub+zip",
            ),
        )

        response = self.client.get(reverse("books:detail", args=[self.book.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("books:download_asset", args=[asset.pk]))
        self.assertNotContains(response, "在线阅读")

    def test_download_route_returns_attachment(self):
        self.client.login(username="asset_admin", password="pass123456")
        asset = BookAsset.objects.create(
            book=self.book,
            asset_type=BookAsset.AssetType.EBOOK,
            visibility=BookAsset.Visibility.LOGIN_REQUIRED,
            download_enabled=True,
            file=SimpleUploadedFile(
                "download.epub",
                b"fake epub bytes",
                content_type="application/epub+zip",
            ),
        )

        response = self.client.get(reverse("books:download_asset", args=[asset.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/epub+zip", response["Content-Type"])
        self.assertIn("attachment", response["Content-Disposition"])


class BookMetadataApiTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Sophie World",
            author="Original Author",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )
        self.staff = User.objects.create_user(
            username="metadata_admin",
            password="pass123456",
            is_staff=True,
        )
        self.viewer = User.objects.create_user(
            username="metadata_viewer",
            password="pass123456",
        )

    def test_preview_requires_editor_permission(self):
        response = self.client.post(
            reverse("books:metadata_preview", args=[self.book.pk]),
            data=json.dumps({"provider": "weread"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_preview_for_non_editor_returns_forbidden(self):
        self.client.login(username="metadata_viewer", password="pass123456")

        response = self.client.post(
            reverse("books:metadata_preview", args=[self.book.pk]),
            data=json.dumps({"provider": "weread"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)

    @patch("apps.books.metadata._lookup_candidate")
    def test_preview_returns_field_diffs_and_preview_token(self, lookup_candidate):
        self.client.login(username="metadata_admin", password="pass123456")
        lookup_candidate.return_value = MetadataCandidate(
            source_id="weread-1",
            title="Sophie World",
            author="Jostein Gaarder",
            translator="Xiao Baosen",
            publisher="Writer Press",
            cover_image_url="https://example.com/cover.jpg",
            short_review="A classic introduction to philosophy.",
        )

        response = self.client.post(
            reverse("books:metadata_preview", args=[self.book.pk]),
            data=json.dumps({"provider": "weread"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "found")
        self.assertEqual(payload["provider"]["id"], "weread")
        self.assertTrue(payload["previewToken"])
        field_names = {field["name"] for field in payload["fields"]}
        self.assertIn("author", field_names)
        self.assertIn("translator", field_names)
        self.assertIn("publisher", field_names)
        self.assertIn("cover_image_url", field_names)

    @patch("apps.books.metadata._lookup_candidate")
    def test_apply_returns_only_selected_fields(self, lookup_candidate):
        self.client.login(username="metadata_admin", password="pass123456")
        lookup_candidate.return_value = MetadataCandidate(
            source_id="douban-1",
            title="Sophie World",
            author="Jostein Gaarder",
            translator="Xiao Baosen",
            publisher="Writer Press",
            cover_image_url="https://example.com/cover.jpg",
            short_review="A classic introduction to philosophy.",
        )

        preview_response = self.client.post(
            reverse("books:metadata_preview", args=[self.book.pk]),
            data=json.dumps({"provider": "douban"}),
            content_type="application/json",
        )
        preview_payload = preview_response.json()

        response = self.client.post(
            reverse("books:metadata_apply", args=[self.book.pk]),
            data=json.dumps(
                {
                    "previewToken": preview_payload["previewToken"],
                    "fields": ["translator", "cover_image_url"],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["updatedFields"], ["translator", "cover_image_url"])
        self.assertEqual(payload["values"]["translator"], "Xiao Baosen")
        self.assertEqual(payload["values"]["cover_image_url"], "https://example.com/cover.jpg")
        self.assertNotIn("author", payload["values"])

    def test_preview_rejects_removed_provider(self):
        self.client.login(username="metadata_admin", password="pass123456")

        response = self.client.post(
            reverse("books:metadata_preview", args=[self.book.pk]),
            data=json.dumps({"provider": "openlibrary"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])

    @patch("apps.books.metadata._lookup_candidate")
    def test_preview_not_found_returns_status(self, lookup_candidate):
        self.client.login(username="metadata_admin", password="pass123456")
        lookup_candidate.return_value = None

        response = self.client.post(
            reverse("books:metadata_preview", args=[self.book.pk]),
            data=json.dumps({"provider": "douban"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "not_found")
        self.assertEqual(payload["provider"]["id"], "douban")


class BookMetadataParsingTests(TestCase):
    @patch("apps.books.metadata._fetch_text")
    def test_douban_lookup_keeps_cover_when_image_uses_data_src(self, fetch_text):
        fetch_text.return_value = """
            <div class="result">
                <div class="pic">
                    <a class="nbg" title="苏菲的世界" onclick="moreurl(this,{ sid: 27172839, qcat: '1001'})">
                        <img data-src="http://img9.doubanio.com/view/subject/s/public/s29580784.jpg">
                    </a>
                </div>
                <div class="content">
                    <span class="subject-cast">[挪威] 乔斯坦·贾德 / 萧宝森 / 作家出版社 / 2017</span>
                    <p>这是一本风靡世界的哲学启蒙书。</p>
                </div>
            </div>
        """

        candidate = _lookup_douban("苏菲的世界", Book(title="苏菲的世界"))

        self.assertIsNotNone(candidate)
        self.assertEqual(
            candidate.cover_image_url,
            "https://img9.doubanio.com/view/subject/s/public/s29580784.jpg",
        )


class BookMetadataBatchApiTests(TestCase):
    def setUp(self):
        self.book_a = Book.objects.create(
            title="Atomic Habits",
            cover_image_url="",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )
        self.book_b = Book.objects.create(
            title="Deep Work",
            cover_image_url="https://example.com/deep-work.jpg",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )
        self.book_c = Book.objects.create(
            title="Missing Book",
            cover_image_url="",
            status=Book.Status.PLANNED,
            visibility=Book.Visibility.PUBLIC,
        )
        self.staff = User.objects.create_user(
            username="batch_admin",
            password="pass123456",
            is_staff=True,
        )

    def test_batch_update_requires_editor_permission(self):
        response = self.client.post(
            reverse("books:batch_metadata_update"),
            data=json.dumps(
                {
                    "provider": "weread",
                    "field": "cover_image_url",
                    "bookIds": [self.book_a.pk],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    @patch("apps.books.metadata._lookup_candidate")
    def test_batch_update_updates_selected_field_and_returns_summary(self, lookup_candidate):
        self.client.login(username="batch_admin", password="pass123456")

        def fake_lookup(provider_id, query, book):
            if book.pk == self.book_a.pk:
                return MetadataCandidate(
                    source_id="weread-a",
                    title=book.title,
                    cover_image_url="https://example.com/atomic-habits.jpg",
                )
            if book.pk == self.book_b.pk:
                return MetadataCandidate(
                    source_id="weread-b",
                    title=book.title,
                    cover_image_url="https://example.com/deep-work.jpg",
                )
            return None

        lookup_candidate.side_effect = fake_lookup

        response = self.client.post(
            reverse("books:batch_metadata_update"),
            data=json.dumps(
                {
                    "provider": "weread",
                    "field": "cover_image_url",
                    "bookIds": [self.book_a.pk, self.book_b.pk, self.book_c.pk],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["summary"]["total"], 3)
        self.assertEqual(payload["summary"]["updated"], 1)
        self.assertEqual(payload["summary"]["unchanged"], 1)
        self.assertEqual(payload["summary"]["not_found"], 1)

        self.book_a.refresh_from_db()
        self.book_b.refresh_from_db()
        self.book_c.refresh_from_db()
        self.assertEqual(self.book_a.cover_image_url, "https://example.com/atomic-habits.jpg")
        self.assertEqual(self.book_b.cover_image_url, "https://example.com/deep-work.jpg")
        self.assertEqual(self.book_c.cover_image_url, "")

    def test_batch_update_rejects_invalid_field(self):
        self.client.login(username="batch_admin", password="pass123456")

        response = self.client.post(
            reverse("books:batch_metadata_update"),
            data=json.dumps(
                {
                    "provider": "weread",
                    "field": "rating",
                    "bookIds": [self.book_a.pk],
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["success"])
