from django.test import TestCase
from django.urls import reverse

from apps.books.models import Book


class HomePageTests(TestCase):
    def test_home_page_renders_latest_book(self):
        Book.objects.create(
            title="沉思录",
            author="马可·奥勒留",
            status=Book.Status.READING,
            short_review="把人安静下来的一本书。",
        )

        response = self.client.get(reverse("home:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "沉思录")
