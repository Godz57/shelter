from django.conf import settings
from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField("nome", max_length=200)
    slug = models.SlugField(unique=True)
    bio = models.TextField(
        "biografia (opcional)",
        blank=True,
        help_text="Texto curto sobre o autor, se quiser.",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "autor"
        verbose_name_plural = "autores"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("catalog:author_detail", kwargs={"slug": self.slug})


class Category(models.Model):
    name = models.CharField("nome", max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "categoria"
        verbose_name_plural = "categorias"

    def __str__(self) -> str:
        return self.name


class Book(models.Model):
    title = models.CharField("título", max_length=255)
    slug = models.SlugField(unique=True)
    subtitle = models.CharField("subtítulo (opcional)", max_length=255, blank=True)
    description = models.TextField(
        "descrição",
        help_text="Resumo do livro para o visitante. Escreva de forma simples.",
    )
    isbn = models.CharField("ISBN (opcional)", max_length=20, blank=True)
    published_date = models.DateField(
        "data de publicação (opcional)",
        null=True,
        blank=True,
        help_text="Se souber, use o formato AAAA-MM-DD (ex.: 2024-05-10).",
    )
    cover_url = models.URLField(
        "link da capa (opcional)",
        blank=True,
        help_text="Cole o link completo da imagem (começa com https://).",
    )
    is_featured = models.BooleanField(
        "destaque na página inicial",
        default=False,
        help_text="Marque para o livro aparecer em destaque na home do site.",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="categoria",
    )
    authors = models.ManyToManyField(
        Author,
        related_name="books",
        blank=True,
        verbose_name="autores",
        help_text="Escolha um ou mais autores na lista ao lado.",
    )
    created_at = models.DateTimeField("criado em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "livro"
        verbose_name_plural = "livros"

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("catalog:book_detail", kwargs={"slug": self.slug})


class ReadingListItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_list",
        verbose_name="leitor",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="on_shelves",
        verbose_name="livro",
    )
    notes = models.CharField(
        "observação (opcional)",
        max_length=255,
        blank=True,
    )
    created_at = models.DateTimeField("salvo em", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "livro salvo"
        verbose_name_plural = "livros salvos pelos leitores"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"], name="unique_user_book_shelf"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.book}"
