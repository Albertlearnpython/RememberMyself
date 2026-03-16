from django.test import TestCase
from django.urls import reverse

from apps.books.models import Book


class HomePageTests(TestCase):
    def test_home_page_renders_memory_streams_with_real_book(self):
        Book.objects.create(
            title="沉思录",
            author="马可·奥勒留",
            status=Book.Status.READING,
            short_review="把人安静下来的一本书。",
            cover_image_url="https://example.com/meditations.jpg",
        )

        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "书影流")
        self.assertContains(response, "声纹流")
        self.assertContains(response, "食味流")
        self.assertContains(response, "风景流")
        self.assertContains(response, "沉思录")
        self.assertNotContains(response, "第一本书录入后，书影流会从这里开始缓慢流动。")

    def test_home_page_shows_empty_books_note_when_library_is_empty(self):
        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "尚未入册")
        self.assertContains(response, "第一本书录入后，书影流会从这里开始缓慢流动。")
