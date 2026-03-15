from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.books.models import Book


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
