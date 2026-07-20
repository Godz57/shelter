from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from catalog.models import Author, Book, Category


class StaffPanelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin",
        )
        self.reader = User.objects.create_user(
            username="reader",
            password="complex-pass-123",
        )
        self.category = Category.objects.create(name="Theology", slug="theology")
        self.author = Author.objects.create(name="Jane Doe", slug="jane-doe")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="A careful look at grace.",
            category=self.category,
        )
        self.book.authors.add(self.author)
        self.client = Client()

    def test_anonymous_redirected_to_login(self):
        res = self.client.get(reverse("staff:dashboard"))
        self.assertEqual(res.status_code, 302)
        self.assertIn("/accounts/login/", res.url)

    def test_non_staff_blocked(self):
        self.client.login(username="reader", password="complex-pass-123")
        res = self.client.get(reverse("staff:dashboard"))
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("catalog:home"))

    def test_staff_dashboard_uses_site_layout(self):
        self.client.login(username="admin", password="admin")
        res = self.client.get(reverse("staff:dashboard"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Manage catalog")
        self.assertContains(res, "Shelter")  # public brand
        self.assertContains(res, "Add book")
        self.assertContains(res, "Grace and Truth")

    def test_staff_can_create_book(self):
        self.client.login(username="admin", password="admin")
        res = self.client.post(
            reverse("staff:book_add"),
            {
                "title": "New Title",
                "subtitle": "",
                "category": self.category.pk,
                "authors": [self.author.pk],
                "description": "A new book for the catalog.",
                "cover_url": "",
                "is_featured": True,
                "isbn": "",
                "published_date": "",
            },
        )
        self.assertEqual(res.status_code, 302)
        book = Book.objects.get(title="New Title")
        self.assertTrue(book.is_featured)
        self.assertEqual(book.slug, "new-title")
        self.assertIn(self.author, book.authors.all())

    def test_staff_can_delete_book(self):
        self.client.login(username="admin", password="admin")
        res = self.client.post(
            reverse("staff:book_delete", kwargs={"slug": self.book.slug})
        )
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())

    def test_no_manage_button_on_public_site(self):
        self.client.login(username="admin", password="admin")
        res = self.client.get(reverse("catalog:home"))
        self.assertNotContains(res, "nav-manage")
        self.assertNotContains(res, ">Manage<")

    def test_staff_login_goes_to_manage_panel(self):
        res = self.client.post(
            reverse("login"),
            {"username": "admin", "password": "admin"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("staff:dashboard"))

    def test_reader_login_goes_to_public_site(self):
        res = self.client.post(
            reverse("login"),
            {"username": "reader", "password": "complex-pass-123"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("catalog:home"))

    def test_old_admin_root_redirects_to_manage(self):
        res = self.client.get("/admin/")
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("staff:dashboard"))

    def test_old_admin_subpath_redirects_to_manage(self):
        res = self.client.get("/admin/catalog/book/")
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("staff:dashboard"))

    def test_old_admin_login_path_redirects_to_manage(self):
        res = self.client.get("/admin/login/")
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res.url, reverse("staff:dashboard"))
