from django.utils.text import slugify


def unique_slug(model, base: str, instance=None, field: str = "slug") -> str:
    """Gera um slug único a partir de um texto (sem o usuário precisar ver isso)."""
    base_slug = slugify(base)[:45] or "item"
    slug = base_slug
    n = 2
    while True:
        qs = model.objects.filter(**{field: slug})
        if instance is not None and instance.pk:
            qs = qs.exclude(pk=instance.pk)
        if not qs.exists():
            return slug
        slug = f"{base_slug}-{n}"
        n += 1
