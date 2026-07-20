from django.test import TestCase

from catalog.models import Book, Category
from catalog.slug_utils import unique_slug


class UniqueSlugTests(TestCase):
    def test_basic_slug(self):
        self.assertEqual(unique_slug(Category, "Teologia"), "teologia")

    def test_collision(self):
        Category.objects.create(name="Teologia", slug="teologia")
        self.assertEqual(unique_slug(Category, "Teologia"), "teologia-2")

    def test_book_from_title(self):
        cat = Category.objects.create(name="X", slug="x")
        Book.objects.create(
            title="Grace and Truth",
            slug="grace-and-truth",
            description="d",
            category=cat,
        )
        self.assertEqual(unique_slug(Book, "Grace and Truth"), "grace-and-truth-2")
