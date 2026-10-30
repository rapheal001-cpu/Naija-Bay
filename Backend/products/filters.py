import django_filters

from .models import Product


def _slug(value):
    """Normalize a slug so ``phones-tablets`` and ``phones_tablets`` match.

    ``Category.slug`` is hyphenated (via ``slugify``) while ``Product.category``
    stores the raw choice key (underscored). Accepting both keeps the public API
    forgiving for clients that copy slugs straight from ``/categories/``.
    """

    if not value:
        return value
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


class ProductFilter(django_filters.FilterSet):
    """Marketplace-style filters mirroring Jiji's category sidebar."""

    category = django_filters.CharFilter(method="filter_category")
    sub_category = django_filters.CharFilter(method="filter_sub_category")
    condition = django_filters.CharFilter(field_name="condition", lookup_expr="iexact")
    state = django_filters.CharFilter(method="filter_state")
    city = django_filters.CharFilter(method="filter_city")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    negotiable = django_filters.BooleanFilter(field_name="negotiable")
    delivery_available = django_filters.BooleanFilter(field_name="delivery_available")
    promoted = django_filters.BooleanFilter(field_name="promoted")
    verified_seller = django_filters.BooleanFilter(field_name="product_user__verified")
    has_images = django_filters.BooleanFilter(method="filter_has_images")
    created_after = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )

    class Meta:
        model = Product
        fields = [
            "category",
            "sub_category",
            "condition",
            "state",
            "city",
            "min_price",
            "max_price",
            "negotiable",
            "delivery_available",
            "promoted",
            "verified_seller",
            "has_images",
            "created_after",
        ]

    def filter_category(self, queryset, name, value):
        return queryset.filter(category__iexact=_slug(value))

    def filter_sub_category(self, queryset, name, value):
        return queryset.filter(sub_category__iexact=_slug(value))

    def filter_state(self, queryset, name, value):
        return queryset.filter(state__iexact=_slug(value))

    def filter_city(self, queryset, name, value):
        return queryset.filter(city__iexact=_slug(value))

    def filter_has_images(self, queryset, name, value):
        if value is True:
            return queryset.filter(images__isnull=False).distinct()
        if value is False:
            return queryset.filter(images__isnull=True)
        return queryset
