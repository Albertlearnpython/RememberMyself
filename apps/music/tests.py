import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from apps.music.models import MusicAsset, MusicTag, MusicTrack


User = get_user_model()


class MusicVisibilityTests(TestCase):
    def setUp(self):
        self.public_track = MusicTrack.objects.create(
            title="公开音乐",
            visibility=MusicTrack.Visibility.PUBLIC,
        )
        self.login_track = MusicTrack.objects.create(
            title="登录可见音乐",
            visibility=MusicTrack.Visibility.LOGIN_REQUIRED,
        )
        self.private_track = MusicTrack.objects.create(
            title="私密音乐",
            visibility=MusicTrack.Visibility.PRIVATE,
        )
        self.user = User.objects.create_user(username="music_viewer", password="pass123456")
        self.staff = User.objects.create_user(
            username="music_editor",
            password="pass123456",
            is_staff=True,
        )

    def test_guest_only_sees_public_tracks(self):
        response = self.client.get(reverse("music:index"))

        self.assertContains(response, "公开音乐")
        self.assertNotContains(response, "登录可见音乐")
        self.assertNotContains(response, "私密音乐")

    def test_authenticated_user_sees_login_required_tracks(self):
        self.client.login(username="music_viewer", password="pass123456")

        response = self.client.get(reverse("music:index"))

        self.assertContains(response, "公开音乐")
        self.assertContains(response, "登录可见音乐")
        self.assertNotContains(response, "私密音乐")

    def test_staff_user_sees_private_tracks_and_editor_entry(self):
        self.client.login(username="music_editor", password="pass123456")

        response = self.client.get(reverse("music:index"))

        self.assertContains(response, "私密音乐")
        self.assertContains(response, "新增音乐")


class MusicAssetTests(TestCase):
    def setUp(self):
        self.temp_media_root = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_media_root)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.temp_media_root, ignore_errors=True))

        self.staff = User.objects.create_user(
            username="music_asset_admin",
            password="pass123456",
            is_staff=True,
        )
        self.track = MusicTrack.objects.create(
            title="夜航星",
            visibility=MusicTrack.Visibility.PUBLIC,
        )
        self.shared_tag = MusicTag.objects.create(name="夜晚")

    def test_create_track_with_upload_creates_asset_and_shared_tags(self):
        self.client.login(username="music_asset_admin", password="pass123456")

        response = self.client.post(
            reverse("music:create"),
            data={
                "title": "起风了",
                "artist": "买辣椒也用券",
                "album": "起风了",
                "cover_image_url": "https://example.com/wind.jpg",
                "tag_links": [self.shared_tag.pk],
                "new_tags": "治愈, 夜晚",
                "short_review": "适合夜里反复听。",
                "why_it_matters": "会把人慢慢带回安静里。",
                "long_note": "第一版只做收藏与归档。",
                "visibility": MusicTrack.Visibility.PUBLIC,
                "asset_visibility": MusicAsset.Visibility.LOGIN_REQUIRED,
                "download_enabled": "on",
                "asset_file": SimpleUploadedFile(
                    "wind.mp3",
                    b"fake mp3 bytes",
                    content_type="audio/mpeg",
                ),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(MusicAsset.objects.count(), 1)
        self.assertEqual(MusicAsset.objects.first().file_extension, ".mp3")
        track = MusicTrack.objects.get(title="起风了")
        self.assertCountEqual(track.tag_list, ["夜晚", "治愈"])
        self.assertEqual(MusicTag.objects.filter(name="夜晚").count(), 1)
        self.assertEqual(MusicTag.objects.count(), 2)

    def test_music_page_can_filter_by_shared_tag(self):
        tagged_track = MusicTrack.objects.create(
            title="夜色钢琴",
            visibility=MusicTrack.Visibility.PUBLIC,
        )
        tagged_track.tag_links.add(self.shared_tag)
        MusicTrack.objects.create(
            title="白天散步歌单",
            visibility=MusicTrack.Visibility.PUBLIC,
        )

        response = self.client.get(reverse("music:index"), {"tag": "夜晚"})

        self.assertContains(response, "夜色钢琴")
        self.assertNotContains(response, "白天散步歌单")

    def test_download_route_returns_attachment(self):
        self.client.login(username="music_asset_admin", password="pass123456")
        asset = MusicAsset.objects.create(
            track=self.track,
            visibility=MusicAsset.Visibility.LOGIN_REQUIRED,
            download_enabled=True,
            file=SimpleUploadedFile(
                "night.mp3",
                b"fake mp3 bytes",
                content_type="audio/mpeg",
            ),
        )

        response = self.client.get(reverse("music:download_asset", args=[asset.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertIn("audio/mpeg", response["Content-Type"])
        self.assertIn("attachment", response["Content-Disposition"])


class MusicHomeStreamTests(TestCase):
    def test_home_page_renders_real_music_stream_item(self):
        MusicTrack.objects.create(
            title="夜航星",
            artist="不才",
            visibility=MusicTrack.Visibility.PUBLIC,
            cover_image_url="https://example.com/night-flight-star.jpg",
        )

        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "夜航星")
