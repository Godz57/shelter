from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .admin_site import shelter_admin_site
from .models import Author, Book, Category, ReadingListItem
from .slug_utils import unique_slug


class SimpleModelAdmin(admin.ModelAdmin):
    """Base: menos opções técnicas, mais clareza."""

    save_on_top = True
    list_per_page = 20
    empty_value_display = "—"
    show_full_result_count = True


@admin.register(Author, site=shelter_admin_site)
class AuthorAdmin(SimpleModelAdmin):
    list_display = ("name", "book_count", "created_at")
    list_display_links = ("name",)
    search_fields = ("name", "bio")
    search_help_text = "Digite o nome do autor para encontrar."
    # slug escondido — gerado sozinho
    exclude = ("slug",)
    readonly_fields = ("created_at",)
    ordering = ("name",)
    fieldsets = (
        (
            "Dados do autor",
            {
                "description": "Preencha o nome. A biografia é opcional.",
                "fields": ("name", "bio"),
            },
        ),
        (
            "Informações do sistema",
            {
                "classes": ("collapse",),
                "fields": ("created_at",),
            },
        ),
    )

    @admin.display(description="Qtd. de livros")
    def book_count(self, obj: Author) -> int:
        return obj.books.count()

    def save_model(self, request, obj, form, change):
        obj.slug = unique_slug(Author, obj.name, instance=obj)
        super().save_model(request, obj, form, change)


@admin.register(Category, site=shelter_admin_site)
class CategoryAdmin(SimpleModelAdmin):
    list_display = ("name", "book_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    search_help_text = "Digite o nome da categoria."
    exclude = ("slug",)
    ordering = ("name",)
    fieldsets = (
        (
            "Categoria",
            {
                "description": (
                    "Ex.: Teologia, Devocional, Biografia. "
                    "Serve para filtrar livros no site."
                ),
                "fields": ("name",),
            },
        ),
    )

    @admin.display(description="Qtd. de livros")
    def book_count(self, obj: Category) -> int:
        return obj.books.count()

    def save_model(self, request, obj, form, change):
        obj.slug = unique_slug(Category, obj.name, instance=obj)
        super().save_model(request, obj, form, change)


@admin.register(Book, site=shelter_admin_site)
class BookAdmin(SimpleModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "category",
        "author_list",
        "is_featured",
        "has_cover",
        "published_date",
    )
    list_display_links = ("title",)
    list_filter = ("is_featured", "category")
    list_editable = ("is_featured",)
    search_fields = ("title", "subtitle", "description", "authors__name")
    search_help_text = "Busque pelo título ou nome do autor."
    filter_horizontal = ("authors",)
    autocomplete_fields = ("category",)
    exclude = ("slug",)
    readonly_fields = ("created_at", "cover_preview", "view_on_site_link")
    ordering = ("-created_at",)
    actions = ("make_featured", "remove_featured")
    date_hierarchy = None  # calendário técnico confunde leigos

    fieldsets = (
        (
            "Sobre o livro",
            {
                "description": "Informações principais que o visitante vê no site.",
                "fields": (
                    "title",
                    "subtitle",
                    "category",
                    "authors",
                    "description",
                    "is_featured",
                ),
            },
        ),
        (
            "Capa do livro",
            {
                "description": (
                    "Cole o endereço (link) de uma imagem na internet. "
                    "Se deixar em branco, o site mostra só a inicial do título."
                ),
                "fields": ("cover_url", "cover_preview"),
            },
        ),
        (
            "Detalhes opcionais",
            {
                "classes": ("collapse",),
                "description": "Pode deixar em branco se não souber.",
                "fields": ("isbn", "published_date"),
            },
        ),
        (
            "Depois de salvar",
            {
                "classes": ("collapse",),
                "fields": ("view_on_site_link", "created_at"),
            },
        ),
    )

    @admin.display(description="Capa")
    def cover_thumb(self, obj: Book) -> str:
        if obj.cover_url:
            return format_html(
                '<img src="{}" alt="" class="shelter-cover-thumb" width="40" height="60" />',
                obj.cover_url,
            )
        initial = (obj.title[:1] or "?").upper()
        return format_html(
            '<span class="shelter-cover-fallback" title="Sem capa">{}</span>',
            initial,
        )

    @admin.display(description="Tem capa?", boolean=True)
    def has_cover(self, obj: Book) -> bool:
        return bool(obj.cover_url)

    @admin.display(description="Prévia da capa")
    def cover_preview(self, obj: Book) -> str:
        if not obj.pk:
            return mark_safe(
                '<p class="shelter-help-box">'
                "Salve o livro uma vez para ver a prévia da capa aqui."
                "</p>"
            )
        if obj.cover_url:
            return format_html(
                '<img src="{}" alt="Capa de {}" class="shelter-cover-preview" />'
                '<p class="shelter-help-muted">Assim a capa aparece no site.</p>',
                obj.cover_url,
                obj.title,
            )
        return mark_safe(
            '<p class="shelter-help-box">'
            "Ainda sem capa — o site usa um quadrado colorido com a letra do título."
            "</p>"
        )

    @admin.display(description="Autores")
    def author_list(self, obj: Book) -> str:
        names = list(obj.authors.values_list("name", flat=True)[:4])
        if not names:
            return "— (adicione autores)"
        text = ", ".join(names)
        extra = obj.authors.count() - len(names)
        if extra > 0:
            text = f"{text} +{extra}"
        return text

    @admin.display(description="Ver no site")
    def view_on_site_link(self, obj: Book) -> str:
        if not obj.pk:
            return "Salve o livro primeiro."
        return format_html(
            '<a class="shelter-btn-link" href="{}" target="_blank" rel="noopener">'
            "Abrir este livro no site ↗</a>",
            obj.get_absolute_url(),
        )

    @admin.action(description="Marcar como destaque na página inicial")
    def make_featured(self, request, queryset):
        n = queryset.update(is_featured=True)
        self.message_user(
            request,
            f"{n} livro(s) agora aparecem em destaque na página inicial.",
        )

    @admin.action(description="Tirar do destaque da página inicial")
    def remove_featured(self, request, queryset):
        n = queryset.update(is_featured=False)
        self.message_user(request, f"Destaque removido de {n} livro(s).")

    def save_model(self, request, obj, form, change):
        obj.slug = unique_slug(Book, obj.title, instance=obj)
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("authors")
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["title"] = "Livros"
        extra_context["shelter_list_hint"] = (
            "Dica: marque “Destaque na página inicial” na lista e clique em Salvar. "
            "Ou selecione vários livros e use a caixa Ação."
        )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ReadingListItem, site=shelter_admin_site)
class ReadingListItemAdmin(SimpleModelAdmin):
    list_display = ("user", "book", "notes_short", "created_at")
    list_filter = ()
    search_fields = ("user__username", "book__title")
    search_help_text = "Busque pelo nome do leitor ou do livro."
    autocomplete_fields = ("user", "book")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Livro salvo pelo leitor",
            {
                "description": (
                    "Aqui ficam os livros que as pessoas colocaram no Your Shelter "
                    "(lista de leitura delas)."
                ),
                "fields": ("user", "book", "notes"),
            },
        ),
        (
            "Quando foi salvo",
            {"classes": ("collapse",), "fields": ("created_at",)},
        ),
    )

    @admin.display(description="Observação")
    def notes_short(self, obj: ReadingListItem) -> str:
        if not obj.notes:
            return "—"
        return obj.notes if len(obj.notes) <= 40 else f"{obj.notes[:37]}…"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user", "book", "book__category")
        )


class SimpleUserAdmin(DjangoUserAdmin):
    """Usuários sem jargão de permissões avançadas na cara."""

    list_display = ("username", "email", "is_staff", "is_active", "last_login")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
    filter_horizontal = ()
    # Menos telas técnicas
    fieldsets = (
        (
            "Conta",
            {
                "description": "Dados de quem pode entrar no painel ou no site.",
                "fields": ("username", "password"),
            },
        ),
        (
            "Nome e e-mail",
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            "Acesso",
            {
                "description": (
                    "“Equipe” libera o painel de administração. "
                    "Só marque se a pessoa deve gerenciar o catálogo."
                ),
                "fields": ("is_active", "is_staff", "is_superuser"),
            },
        ),
        (
            "Datas",
            {"classes": ("collapse",), "fields": ("last_login", "date_joined")},
        ),
    )
    add_fieldsets = (
        (
            "Nova conta",
            {
                "classes": ("wide",),
                "description": "Crie um usuário. Se for da equipe, marque “Equipe” depois de salvar.",
                "fields": ("username", "password1", "password2"),
            },
        ),
    )


# Só usuários — sem “Groups” (muito técnico para leigos)
shelter_admin_site.register(User, SimpleUserAdmin)
