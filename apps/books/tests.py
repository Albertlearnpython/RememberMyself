import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.books.models import Book, BookAsset


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
            status=Book.Status.PAUSED,
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


class BookAssetReaderTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

        self.staff = User.objects.create_user(
            username="reader_admin",
            password="pass123456",
            is_staff=True,
        )
        self.book = Book.objects.create(
            title="EPUB 测试书",
            status=Book.Status.READING,
            visibility=Book.Visibility.PUBLIC,
        )

    def test_create_book_with_epub_upload_creates_asset(self):
        self.client.login(username="reader_admin", password="pass123456")

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
                "rating": "",
                "tags": "",
                "short_review": "",
                "why_it_matters": "",
                "long_note": "",
                "reading_started_at": "",
                "reading_finished_at": "",
                "visibility": Book.Visibility.PUBLIC,
                "asset_type": BookAsset.AssetType.EBOOK,
                "asset_visibility": BookAsset.Visibility.LOGIN_REQUIRED,
                "reader_enabled": "on",
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

    def test_epub_read_route_renders_reader_page(self):
        self.client.login(username="reader_admin", password="pass123456")
        asset = BookAsset.objects.create(
            book=self.book,
            asset_type=BookAsset.AssetType.EBOOK,
            visibility=BookAsset.Visibility.LOGIN_REQUIRED,
            reader_enabled=True,
            download_enabled=True,
            file=SimpleUploadedFile(
                "reader.epub",
                b"fake epub bytes",
                content_type="application/epub+zip",
            ),
        )

        response = self.client.get(reverse("books:read_asset", args=[asset.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "books/reader.html")
        self.assertContains(response, reverse("books:stream_asset", args=[asset.pk]))

    def test_epub_stream_route_returns_epub_content_type(self):
        self.client.login(username="reader_admin", password="pass123456")
        asset = BookAsset.objects.create(
            book=self.book,
            asset_type=BookAsset.AssetType.EBOOK,
            visibility=BookAsset.Visibility.LOGIN_REQUIRED,
            reader_enabled=True,
            download_enabled=True,
            file=SimpleUploadedFile(
                "stream.epub",
                b"fake epub bytes",
                content_type="application/epub+zip",
            ),
        )

        response = self.client.get(reverse("books:stream_asset", args=[asset.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/epub+zip", response["Content-Type"])
