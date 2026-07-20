from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import reverse


class ShelterAdminSite(admin.AdminSite):
    """Painel simples para quem não é programador."""

    site_header = "Your Shelter"
    site_title = "Your Shelter"
    index_title = "Início"
    site_url = "/"
    # Barra lateral técnica do Django desligada
    enable_nav_sidebar = False

    def each_context(self, request):
        context = super().each_context(request)
        from .models import Author, Book, Category, ReadingListItem

        User = get_user_model()
        context["shelter_stats"] = {
            "books": Book.objects.count(),
            "featured": Book.objects.filter(is_featured=True).count(),
            "authors": Author.objects.count(),
            "categories": Category.objects.count(),
            "saved": ReadingListItem.objects.count(),
            "missing_covers": Book.objects.filter(cover_url="").count(),
        }
        # Menu principal em português, linguagem do dia a dia
        context["shelter_menu"] = [
            {
                "label": "Livros",
                "url": reverse("admin:catalog_book_changelist"),
                "hint": "Ver, editar ou apagar livros do catálogo",
                "cta": "Abrir lista",
                "icon": "book",
                "primary": True,
            },
            {
                "label": "Novo livro",
                "url": reverse("admin:catalog_book_add"),
                "hint": "Cadastrar um livro novo no site",
                "cta": "Cadastrar",
                "icon": "add",
                "primary": True,
            },
            {
                "label": "Autores",
                "url": reverse("admin:catalog_author_changelist"),
                "hint": "Quem escreveu os livros",
                "cta": "Ver autores",
                "icon": "author",
            },
            {
                "label": "Categorias",
                "url": reverse("admin:catalog_category_changelist"),
                "hint": "Temas (teologia, devocional…)",
                "cta": "Ver categorias",
                "icon": "tag",
            },
            {
                "label": "Listas dos leitores",
                "url": reverse("admin:catalog_readinglistitem_changelist"),
                "hint": "Livros que as pessoas salvaram no Your Shelter",
                "cta": "Ver listas",
                "icon": "heart",
            },
            {
                "label": "Ver o site",
                "url": "/",
                "hint": "Abre o site público (como o visitante vê)",
                "cta": "Abrir site",
                "icon": "site",
                "external": True,
            },
        ]
        context["shelter_steps"] = [
            "1. Crie uma categoria (se ainda não existir).",
            "2. Cadastre o autor do livro.",
            "3. Cadastre o livro e, se quiser, cole o link da capa.",
            "4. Marque “Destaque na página inicial” para aparecer em Featured.",
            "5. Clique em Salvar e confira no site.",
        ]
        # Esconde a lista técnica de apps no index (usamos só os cards)
        context["available_apps"] = []
        return context

    def get_app_list(self, request, app_label=None):
        """Remove apps de autenticação da navegação residual."""
        app_list = super().get_app_list(request, app_label=app_label)
        # Mantém só o catálogo se algo ainda pedir app_list
        return [app for app in app_list if app.get("app_label") == "catalog"]


shelter_admin_site = ShelterAdminSite(name="admin")
