import shutil
import tempfile
from io import BytesIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from PIL import Image

from apps.scenery.models import SceneryEntry, SceneryPhoto


User = get_user_model()


def build_test_image(name="scenery.jpg", color=(56, 114, 168)):
    buffer = BytesIO()
    image = Image.new("RGB", (1200, 900), color)
    image.save(buffer, format="JPEG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/jpeg")


class SceneryVisibilityTests(TestCase):
    def setUp(self):
        self.public_entry = SceneryEntry.objects.create(title="公开景色", visibility=SceneryEntry.Visibility.PUBLIC)
        self.login_entry = SceneryEntry.objects.create(title="登录景色", visibility=SceneryEntry.Visibility.LOGIN_REQUIRED)
        self.private_entry = SceneryEntry.objects.create(title="私密景色", visibility=SceneryEntry.Visibility.PRIVATE)
        self.user = User.objects.create_user(username="scenery_viewer", password="pass123456")
        self.staff = User.objects.create_user(
            username="scenery_editor",
            password="pass123456",
            is_staff=True,
        )

    def test_guest_only_sees_public_entries(self):
        response = self.client.get(reverse("scenery:index"))

        self.assertContains(response, "公开景色")
        self.assertNotContains(response, "登录景色")
        self.assertNotContains(response, "私密景色")

    def test_authenticated_user_sees_login_required_entries(self):
        self.client.login(username="scenery_viewer", password="pass123456")

        response = self.client.get(reverse("scenery:index"))

        self.assertContains(response, "公开景色")
        self.assertContains(response, "登录景色")
        self.assertNotContains(response, "私密景色")

    def test_staff_user_sees_private_entries_and_editor_entry(self):
        self.client.login(username="scenery_editor", password="pass123456")

        response = self.client.get(reverse("scenery:index"))

        self.assertContains(response, "私密景色")
        self.assertContains(response, "新增景色")


class SceneryUploadTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

        self.staff = User.objects.create_user(
            username="scenery_asset_admin",
            password="pass123456",
            is_staff=True,
        )

    @patch("apps.scenery.services.reverse_geocode")
    def test_create_entry_with_upload_auto_fills_place_and_photo(self, reverse_geocode):
        reverse_geocode.return_value = {
            "country": "中国",
            "province": "广东省",
            "city": "深圳市",
            "district": "南山区",
            "place_name": "深圳湾公园",
            "location_text": "深圳湾公园，深圳市，广东省，中国",
        }
        self.client.login(username="scenery_asset_admin", password="pass123456")

        response = self.client.post(
            reverse("scenery:create"),
            data={
                "title": "",
                "short_note": "晚风刚好。",
                "why_it_matters": "那天整个人很安静。",
                "long_note": "第一版先把上传、识别和展示接起来。",
                "place_name": "",
                "location_text": "",
                "country": "",
                "province": "",
                "city": "",
                "district": "",
                "latitude": "",
                "longitude": "",
                "visibility": SceneryEntry.Visibility.PUBLIC,
                "photos": [build_test_image()],
            },
        )

        self.assertEqual(response.status_code, 302)
        entry = SceneryEntry.objects.get()
        self.assertEqual(entry.photo_count, 1)
        self.assertTrue(entry.title)
        self.assertEqual(SceneryPhoto.objects.count(), 1)

    def test_photo_image_route_returns_inline_image(self):
        self.client.login(username="scenery_asset_admin", password="pass123456")
        entry = SceneryEntry.objects.create(title="海边", visibility=SceneryEntry.Visibility.PUBLIC)
        photo = SceneryPhoto.objects.create(
            entry=entry,
            image=build_test_image(),
            original_filename="sea.jpg",
            width=1200,
            height=900,
        )

        response = self.client.get(reverse("scenery:photo_image", args=[photo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")

    def test_entry_without_photos_is_rejected_on_create(self):
        self.client.login(username="scenery_asset_admin", password="pass123456")

        response = self.client.post(
            reverse("scenery:create"),
            data={
                "title": "空景色",
                "visibility": SceneryEntry.Visibility.PUBLIC,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "至少上传一张图片")
        self.assertFalse(SceneryEntry.objects.filter(title="空景色").exists())


class SceneryHomeStreamTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

    def test_home_page_renders_real_scenery_stream_item(self):
        entry = SceneryEntry.objects.create(
            title="山顶晚霞",
            city="深圳",
            visibility=SceneryEntry.Visibility.PUBLIC,
        )
        SceneryPhoto.objects.create(
            entry=entry,
            image=build_test_image(),
            original_filename="sunset.jpg",
            width=1200,
            height=900,
        )

        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "山顶晚霞")

