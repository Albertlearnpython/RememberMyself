import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.articles.models import ArticleEntry


User = get_user_model()


class ArticleVisibilityTests(TestCase):
    def setUp(self):
        self.public_article = ArticleEntry.objects.create(
            title="公开文章",
            markdown_content="# 公开内容",
            visibility=ArticleEntry.Visibility.PUBLIC,
        )
        self.login_article = ArticleEntry.objects.create(
            title="登录可见文章",
            markdown_content="# 登录内容",
            visibility=ArticleEntry.Visibility.LOGIN_REQUIRED,
        )
        self.private_article = ArticleEntry.objects.create(
            title="私密文章",
            markdown_content="# 私密内容",
            visibility=ArticleEntry.Visibility.PRIVATE,
        )
        self.user = User.objects.create_user(username="article_viewer", password="pass123456")
        self.staff = User.objects.create_user(
            username="article_editor",
            password="pass123456",
            is_staff=True,
        )

    def test_guest_only_sees_public_articles(self):
        response = self.client.get(reverse("articles:index"))

        self.assertContains(response, "公开文章")
        self.assertNotContains(response, "登录可见文章")
        self.assertNotContains(response, "私密文章")

    def test_authenticated_user_sees_login_required_articles(self):
        self.client.login(username="article_viewer", password="pass123456")

        response = self.client.get(reverse("articles:index"))

        self.assertContains(response, "公开文章")
        self.assertContains(response, "登录可见文章")
        self.assertNotContains(response, "私密文章")

    def test_staff_user_sees_private_articles_and_editor_entry(self):
        self.client.login(username="article_editor", password="pass123456")

        response = self.client.get(reverse("articles:index"))

        self.assertContains(response, "私密文章")
        self.assertContains(response, "新增文章")


class ArticleAssetTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

        self.staff = User.objects.create_user(
            username="article_asset_admin",
            password="pass123456",
            is_staff=True,
        )

    def test_create_article_with_markdown_upload_and_download(self):
        self.client.login(username="article_asset_admin", password="pass123456")

        response = self.client.post(
            reverse("articles:create"),
            data={
                "title": "第一篇文章",
                "summary": "这是摘要",
                "markdown_content": "",
                "visibility": ArticleEntry.Visibility.PUBLIC,
                "source_upload": SimpleUploadedFile(
                    "first-note.md",
                    b"# Hello\n\nThis is **markdown**.",
                    content_type="text/markdown",
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        article = ArticleEntry.objects.get(title="第一篇文章")
        self.assertEqual(article.source_filename, "first-note.md")
        self.assertIn("This is **markdown**.", article.markdown_content)

        download_response = self.client.get(reverse("articles:download_source", args=[article.pk]))
        self.assertEqual(download_response.status_code, 200)
        self.assertIn("attachment", download_response["Content-Disposition"])
        self.assertIn("first-note.md", download_response["Content-Disposition"])

    def test_edit_article_overwrites_existing_source_file(self):
        self.client.login(username="article_asset_admin", password="pass123456")
        article = ArticleEntry.objects.create(
            title="覆盖测试",
            summary="旧摘要",
            markdown_content="# Old\n\nOld body",
            visibility=ArticleEntry.Visibility.PUBLIC,
        )
        self.client.post(
            reverse("articles:edit", args=[article.pk]),
            data={
                "title": "覆盖测试",
                "summary": "旧摘要",
                "markdown_content": "# Old\n\nOld body",
                "visibility": ArticleEntry.Visibility.PUBLIC,
            },
        )
        article.refresh_from_db()
        original_name = article.source_file.name

        response = self.client.post(
            reverse("articles:edit", args=[article.pk]),
            data={
                "title": "覆盖测试",
                "summary": "新摘要",
                "markdown_content": "# Changed\n\nUpdated body",
                "visibility": ArticleEntry.Visibility.PUBLIC,
            },
        )

        self.assertEqual(response.status_code, 302)
        article.refresh_from_db()
        self.assertEqual(article.source_file.name, original_name)
        with article.source_file.open("rb") as file_handle:
            content = file_handle.read().decode("utf-8")
        self.assertIn("Updated body", content)

    def test_detail_page_renders_markdown_html(self):
        article = ArticleEntry.objects.create(
            title="渲染测试",
            markdown_content="# 正文标题\n\n- 条目一",
            visibility=ArticleEntry.Visibility.PUBLIC,
        )

        response = self.client.get(reverse("articles:detail", args=[article.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>正文标题</h1>", html=True)
        self.assertContains(response, "<li>条目一</li>", html=True)


class ArticleHomeStreamTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

    def test_home_page_renders_real_article_stream_item(self):
        ArticleEntry.objects.create(
            title="用文章把思路留下来",
            summary="Markdown 文章已经接入首页溪流。",
            markdown_content="# 用文章把思路留下来",
            visibility=ArticleEntry.Visibility.PUBLIC,
        )

        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "用文章把思路留下来")

