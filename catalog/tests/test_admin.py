from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from catalog.admin import BookAdmin
from catalog.admin_site import shelter_admin_site
from catalog.models import Author, Book, Category, ReadingListItem
from catalog.slug_utils import unique_slug


class AdminRegistrationTests(TestCase):
    def test_models_registered(self):
        for model in (Author, Category, Book, ReadingListItem):
            self.assertTrue(shelter_admin_site.is_registered(model))

    def test_admin_branding_and_no_sidebar(self):
        self.assertEqual(shelter_admin_site.site_header, "Your Shelter")
        self.assertFalse(shelter_admin_site.enable_nav_sidebar)


class SlugUtilsTests(TestCase):
    def test_unique_slug(self):
        Category.objects.create(name="Theology", slug="theology")
        slug = unique_slug(Category, "Theology")
        self.assertEqual(slug, "theology-2")


class BookAdminDisplayTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Theology", slug="theology")
        self.book = Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="Sample description for tests.",
            category=self.category,
            cover_url="https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=200",
        )
        self.book_admin = BookAdmin(Book, shelter_admin_site)

    def test_cover_thumb_uses_img(self):
        html = self.book_admin.cover_thumb(self.book)
        self.assertIn("<img", html)
        self.assertIn(self.book.cover_url, html)

    def test_cover_thumb_fallback_without_url(self):
        self.book.cover_url = ""
        html = self.book_admin.cover_thumb(self.book)
        self.assertIn("shelter-cover-fallback", html)
        self.assertIn("G", html)

    def test_slug_hidden_from_fields(self):
        self.assertIn("slug", self.book_admin.exclude)


class AdminSmokeTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin",
        )
        self.client = Client()
        self.client.login(username="admin", password="admin")
        cat = Category.objects.create(name="Theology", slug="theology")
        Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="d",
            category=cat,
        )

    def test_admin_index_is_simple_dashboard(self):
        res = self.client.get(reverse("admin:index"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "O que você quer fazer?")
        self.assertContains(res, "Cadastrar livro")
        self.assertContains(res, "passo a passo")
        # Sem a lista técnica padrão de apps Django
        self.assertNotContains(res, "Authentication and Authorization")
        self.assertNotContains(res, "Recent actions")

    def test_top_nav_present(self):
        res = self.client.get(reverse("admin:index"))
        self.assertContains(res, "shelter-top-nav")
        self.assertContains(res, "Livros")
        self.assertContains(res, "Novo livro")

    def test_book_changelist_loads(self):
        res = self.client.get(reverse("admin:catalog_book_changelist"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Grace and Truth")

    def test_login_page_portuguese(self):
        self.client.logout()
        res = self.client.get(reverse("admin:login"))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Entrar no painel")
