"""Reusable queryset composers for Naija-Bay (SkillStream pattern).

Every list/detail queryset in the codebase goes through one of these helpers
so per-row data (sellers, ratings, favorites, attributes, messages, payments)
is fetched in a constant number of batched queries — never an N+1.

Usage examples::

    qs = with_listing_context(Product.objects.filter(active=True))
    qs = with_conversation_context(Conversation.objects.filter(buyer=user))

Helpers are pure composers: they return modified querysets without
evaluating them, so they chain with ``.filter()``, ``.annotate()`` and
pagination in any order.
"""

from django.db.models import Count, IntegerField, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import Coalesce

LISTING_PREFETCH = (
    "views",
    "favorites",
    "images",
    "ratings",
)


def _attribute_values_prefetch():
    """Attribute rows with their definitions, as an in-memory list.

    ``to_attr`` stores a plain list so serializers never issue per-row queries.
    """
    from products.models import ProductAttribute

    return Prefetch(
        "attribute_values",
        queryset=ProductAttribute.objects.select_related("definition"),
        to_attr="prefetched_attribute_values",
    )


def count_subquery(model, fk_field, **filters):
    """Correlated ``COUNT(...)`` over a foreign-key related model."""
    return Coalesce(
        Subquery(
            model.objects.filter(**{fk_field: OuterRef("pk")}, **filters)
            .order_by()
            .values(fk_field)
            .annotate(total=Count("pk"))
            .values("total")[:1],
            output_field=IntegerField(),
        ),
        0,
        output_field=IntegerField(),
    )


def with_listing_context(queryset):
    """Product rows with seller+store, images, ratings and attribute values."""
    from accounts.models import User
    from products.models import ProductImage, ProductRating

    return queryset.select_related("product_user", "product_user__store").prefetch_related(
        *LISTING_PREFETCH,
        Prefetch("favorites", queryset=User.objects.only("pk"), to_attr="prefetched_favorites"),
        Prefetch("views", queryset=User.objects.only("pk"), to_attr="prefetched_views"),
        Prefetch("images", queryset=ProductImage.objects.all(), to_attr="prefetched_images"),
        Prefetch("ratings", queryset=ProductRating.objects.select_related("user"), to_attr="prefetched_ratings"),
        _attribute_values_prefetch(),
    )


def with_rating_aggregates(queryset):
    """SQL-side rating aggregates (avg/count/distinct) when annotation is cheap."""
    from django.db.models import Avg

    return queryset.annotate(
        _average_rating=Avg("ratings__value"),
        _total_ratings=Count("ratings", distinct=True),
    )


def with_category_context(queryset):
    """Category/subcategory trees for breadcrumb + nav rendering."""
    return queryset.prefetch_related("sub_categories")


def with_cart_context(queryset):
    """Cart rows with product data + images (single batched hit)."""
    return queryset.select_related("product", "product__product_user").prefetch_related(
        "product__images"
    )


def with_order_context(queryset):
    """Orders with items, product images, sellers and payments (cached)."""
    return queryset.prefetch_related(
        "items",
        "items__product__images",
        "items__seller",
        "payments",
    )


def with_conversation_context(queryset, user):
    """Conversations with counterpart, product image, senders + unread count."""
    return (
        queryset.select_related(
            "product", "buyer", "seller", "buyer__store", "seller__store"
        )
        .prefetch_related("messages__sender", "product__images")
        .annotate(
            _annotated_unread_count=Count(
                "messages",
                filter=Q(messages__read=False) & ~Q(messages__sender=user),
                distinct=True,
            )
        )
    )


def with_seller_context(queryset):
    """Seller profile/store queries with products + followers in one hit."""
    return queryset.select_related("store").prefetch_related(
        "products",
        "products__images",
        "favorite_products",
        "favorite_products__images",
    )
