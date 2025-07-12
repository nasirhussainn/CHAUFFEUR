from slugify import slugify

def generate_unique_slug(instance, base_value: str, slug_field: str = 'slug') -> str:
    base_slug = slugify(base_value)
    slug = base_slug
    num = 1
    ModelClass = instance.__class__

    # Keep modifying the slug until it's unique
    while ModelClass.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{num}"
        num += 1

    return slug
