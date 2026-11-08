import datetime
from datetime import timedelta

from django.db import models, transaction
from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import status
from decimal import Decimal
from rest_framework.exceptions import ValidationError
from rest_framework.generics import (
    get_object_or_404,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from .filters import ProductFilter
from .serializers import (
    ProductImageSerializer,
    ProductSerializer,
    CategorySerializer,
    ProductReportSerializer,
    ProductRatingSerializer,
)
from .models import Product, ProductImage, ProductReport, ProductRating
from core.models import AttributeDefinition, Category
from NaijaBay.cache import CATEGORY_LIST_CACHE, cached_read_list
from NaijaBay.queryset_helper import with_category_context, with_listing_context, with_rating_aggregates
from NaijaBay.pagination import StandardPagination
from NaijaBay.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from payments.services import expire_boosts_if_due
from NaijaBay.throttling import (
    ProductThrottling,
    CreateProductThrottling,
    ReportThrottling,
)


# =============================================================================
# GENERAL
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["Products"], operation_id="Products"))
class ProductsListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ProductThrottling]
    pagination_class = StandardPagination
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_class = ProductFilter
    search_fields = [
        "product_name",
        "description",
        "category",
        "sub_category",
        "condition",
        "state",
        "city",
        "category_obj__name",
        "subcategory_obj__name",
    ]

    def get_queryset(self):
        # Switch off paid boosts that have run out (cheap: runs at most once a minute).
        expire_boosts_if_due()
        now = timezone.now()
        return (
            with_rating_aggregates(
                with_listing_context(
                    Product.objects.filter(active=True, sold=False)
                    .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
                )
            )
            .order_by("-created_at")
        )

    # ------------------------------------------------------------------
    # Dynamic attribute filters (Stage 3B)
    # ------------------------------------------------------------------
    # Query shapes (all optional, combined with AND):
    #   attr_<slug>=value              exact match (select/text/number/boolean/date)
    #   attr_<slug>__in=a,b,c          any-of (select/text; multiselect: contains)
    #   attr_<slug>_min= / _max=       numeric/date range
    # Only definitions marked filterable=True are honored; unknown or
    # non-filterable params are ignored (never a 400 for typos).

    def _attribute_definitions(self):
        """Filterable definitions for the current request's category scope."""
        qs = AttributeDefinition.objects.filter(filterable=True)
        raw_category = self.request.query_params.get("category") or self.request.query_params.get("category_obj")
        if raw_category:
            normalized = str(raw_category).strip().lower().replace("_", "-")
            category = Category.objects.filter(slug=normalized).first()
            if category:
                qs = qs.filter(category=category)
                raw_sub = self.request.query_params.get("sub_category")
                if raw_sub:
                    sub_slug = str(raw_sub).strip().lower().replace("_", "-")
                    qs = qs.filter(
                        Q(sub_category__isnull=True)
                        | Q(sub_category__slug=sub_slug, sub_category__category=category)
                    )
                else:
                    qs = qs.filter(sub_category__isnull=True)
        return qs

    def _parse_number(self, param, raw):
        try:
            return Decimal(str(raw))
        except Exception:
            raise ValidationError({param: "Must be a number."})

    def _parse_date(self, param, raw):
        try:
            return datetime.date.fromisoformat(str(raw))
        except ValueError:
            raise ValidationError({param: "Must be an ISO date (YYYY-MM-DD)."})

    def _filter_attributes(self, queryset):
        params = self.request.query_params
        attr_params = {
            key: value
            for key, value in params.items()
            if key.startswith("attr_")
        }
        if not attr_params:
            return queryset

        definitions = {
            f"attr_{d.slug}": d for d in self._attribute_definitions()
        }
        # Build lookup including suffixed keys (handled below per definition).
        base_by_slug = {d.slug: d for d in self._attribute_definitions()}

        for key, raw in attr_params.items():
            slug = key[len("attr_"):]
            if slug.endswith("__in"):
                slug, mode = slug[: -len("__in")], "in"
            elif slug.endswith("_min"):
                slug, mode = slug[: -len("_min")], "min"
            elif slug.endswith("_max"):
                slug, mode = slug[: -len("_max")], "max"
            else:
                mode = "exact"

            definition = base_by_slug.get(slug)
            if definition is None:
                continue  # unknown or non-filterable: ignore silently

            join = "attribute_values"
            typed = {
                "number": "value_number",
                "decimal": "value_number",
                "boolean": "value_bool",
                "date": "value_date",
                "select": "value_text",
                "multiselect": "value_list",
                "text": "value_text",
            }[definition.data_type]
            field = f"{join}__{typed}"

            if mode == "min":
                if definition.data_type in ("number", "decimal"):
                    queryset = queryset.filter(**{f"{field}__gte": self._parse_number(key, raw)})
                elif definition.data_type == "date":
                    queryset = queryset.filter(**{f"{field}__gte": self._parse_date(key, raw)})
                else:
                    continue
            elif mode == "max":
                if definition.data_type in ("number", "decimal"):
                    queryset = queryset.filter(**{f"{field}__lte": self._parse_number(key, raw)})
                elif definition.data_type == "date":
                    queryset = queryset.filter(**{f"{field}__lte": self._parse_date(key, raw)})
                else:
                    continue
            elif mode == "in":
                values = [v.strip() for v in str(raw).split(",") if v.strip()]
                if definition.data_type == "multiselect":
                    cond = Q()
                    for v in values:
                        cond |= Q(**{f"{field}__icontains": v})
                    queryset = queryset.filter(cond)
                elif typed == "value_number":
                    numbers = [self._parse_number(key, v) for v in values]
                    queryset = queryset.filter(**{f"{field}__in": numbers})
                elif typed == "value_bool":
                    bools = [self._parse_bool(key, v) for v in values]
                    queryset = queryset.filter(**{f"{field}__in": bools})
                else:
                    queryset = queryset.filter(**{f"{field}__in": values})
            else:  # exact
                if typed == "value_number":
                    queryset = queryset.filter(**{field: self._parse_number(key, raw)})
                elif typed == "value_bool":
                    queryset = queryset.filter(**{field: self._parse_bool(key, raw)})
                elif typed == "value_date":
                    queryset = queryset.filter(**{field: self._parse_date(key, raw)})
                elif typed == "value_list":
                    queryset = queryset.filter(**{f"{field}__icontains": str(raw).strip()})
                else:
                    queryset = queryset.filter(**{field: str(raw).strip()})

        return queryset.distinct()

    def _parse_bool(self, param, raw):
        lowered = str(raw).strip().lower()
        if lowered in ("true", "1", "yes"):
            return True
        if lowered in ("false", "0", "no"):
            return False
        raise ValidationError({param: "Must be true or false."})

    # ------------------------------------------------------------------
    # Facet counts (Stage 3C): {slug: {option_value: product_count}}
    # ------------------------------------------------------------------

    def _apply_attr_param(self, queryset, definition, mode, key, raw):
        """Apply one attr_* param for one definition; returns queryset."""
        typed = {
            "number": "value_number",
            "decimal": "value_number",
            "boolean": "value_bool",
            "date": "value_date",
            "select": "value_text",
            "multiselect": "value_list",
            "text": "value_text",
        }[definition.data_type]
        field = f"attribute_values__{typed}"

        if mode == "min":
            if definition.data_type in ("number", "decimal"):
                return queryset.filter(**{f"{field}__gte": self._parse_number(key, raw)})
            if definition.data_type == "date":
                return queryset.filter(**{f"{field}__gte": self._parse_date(key, raw)})
            return queryset
        if mode == "max":
            if definition.data_type in ("number", "decimal"):
                return queryset.filter(**{f"{field}__lte": self._parse_number(key, raw)})
            if definition.data_type == "date":
                return queryset.filter(**{f"{field}__lte": self._parse_date(key, raw)})
            return queryset
        if mode == "in":
            values = [v.strip() for v in str(raw).split(",") if v.strip()]
            if definition.data_type == "multiselect":
                cond = Q()
                for v in values:
                    cond |= Q(**{f"{field}__icontains": v})
                return queryset.filter(cond)
            if typed == "value_number":
                return queryset.filter(**{f"{field}__in": [self._parse_number(key, v) for v in values]})
            if typed == "value_bool":
                return queryset.filter(**{f"{field}__in": [self._parse_bool(key, v) for v in values]})
            return queryset.filter(**{f"{field}__in": values})

        # exact
        if typed == "value_number":
            return queryset.filter(**{field: self._parse_number(key, raw)})
        if typed == "value_bool":
            return queryset.filter(**{field: self._parse_bool(key, raw)})
        if typed == "value_date":
            return queryset.filter(**{field: self._parse_date(key, raw)})
        if typed == "value_list":
            return queryset.filter(**{f"{field}__icontains": str(raw).strip()})
        return queryset.filter(**{field: str(raw).strip()})

    def _attr_param_groups(self):
        """Group attr_* query params by definition slug."""
        groups = {}
        for key, value in self.request.query_params.items():
            if not key.startswith("attr_"):
                continue
            slug = key[len("attr_"):]
            if slug.endswith("__in"):
                slug, mode = slug[: -len("__in")], "in"
            elif slug.endswith("_min"):
                slug, mode = slug[: -len("_min")], "min"
            elif slug.endswith("_max"):
                slug, mode = slug[: -len("_max")], "max"
            else:
                mode = "exact"
            groups.setdefault(slug, []).append((mode, key, value))
        return groups

    def _compute_facets(self, base_queryset):
        """Per-option tallies for filterable select definitions in scope.

        Standard faceted-search semantics: each definition is counted over
        the base queryset (filterset filters) plus every attr filter EXCEPT
        its own, so toggling an option never collapses its own counts.
        Numbers/dates are excluded — they render as ranges in the UI.
        """
        from products.models import ProductAttribute

        groups = self._attr_param_groups()
        by_slug = {d.slug: d for d in self._attribute_definitions()}
        facets = {}
        for slug, definition in by_slug.items():
            if definition.data_type not in ("select", "multiselect"):
                continue
            qs = base_queryset
            for other_slug, specs in groups.items():
                if other_slug == slug:
                    continue
                other_def = by_slug.get(other_slug)
                if other_def is None:
                    continue
                for mode, key, raw in specs:
                    qs = self._apply_attr_param(qs, other_def, mode, key, raw)
            options = definition.options.values_list("value", flat=True)
            if definition.data_type == "multiselect":
                counts = {}
                for option_value in options:
                    counts[option_value] = ProductAttribute.objects.filter(
                        product_id__in=qs.values("id"),
                        definition=definition,
                        value_list__icontains=option_value,
                    ).count()
                facets[slug] = counts
                continue
            rows = (
                ProductAttribute.objects.filter(
                    product_id__in=qs.values("id"),
                    definition=definition,
                    value_text__isnull=False,
                )
                .values("value_text")
                .annotate(n=Count("id"))
            )
            counts = {row["value_text"]: row["n"] for row in rows}
            facets[slug] = {v: counts.get(v, 0) for v in options}
        return {k: facets[k] for k in sorted(facets)}

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        if getattr(self, "_pending_facets", None) is not None and hasattr(response.data, "keys"):
            response.data["facets"] = self._pending_facets
        return response

    def filter_queryset(self, queryset):
        base = super().filter_queryset(queryset)
        if (self.request.query_params.get("facets") or "").lower() in ("1", "true"):
            self._pending_facets = self._compute_facets(base)
        queryset = self._filter_attributes(base)
        sort = (self.request.query_params.get("sort") or "").lower()

        if sort == "price_asc":
            return queryset.order_by("-promoted", "-boost_level", "price", "-created_at")
        if sort == "price_desc":
            return queryset.order_by("-promoted", "-boost_level", "-price", "-created_at")
        if sort == "oldest":
            return queryset.order_by("-promoted", "-boost_level", "created_at")
        if sort in ("popular", "views"):
            return queryset.annotate(
                _views_total=Count("views", distinct=True)
            ).order_by("-promoted", "-boost_level", "-_views_total", "-created_at")
        if sort == "favorites":
            return queryset.annotate(
                _favorites_total=Count("favorites", distinct=True)
            ).order_by("-promoted", "-boost_level", "-_favorites_total", "-created_at")

        # Default: promoted listings first, then newest.
        return queryset.order_by("-promoted", "-boost_level", "-created_at")


products_list_view = ProductsListAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Featured Products")
)
class FeaturedProductsListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ProductThrottling]
    pagination_class = None

    def get_queryset(self):
        return (
            with_listing_context(
                Product.objects.filter(active=True, sold=False)
            )
            .order_by("-created_at")[:50]
        )

featured_products_view = FeaturedProductsListAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Flash Deals")
)
class FlashDealsListAPIView(ListAPIView):
    """Discounted listings, biggest savings first — powers the homepage flash-deals rail."""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ProductThrottling]
    pagination_class = None

    def get_queryset(self):
        now = timezone.now()
        return (
            with_rating_aggregates(
                with_listing_context(
                    Product.objects.filter(active=True, sold=False, original_price__gt=0)
                    .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
                    .filter(original_price__gt=models.F("price"))
                )
            )
            .order_by("-promoted", "-boost_level", "price")[:50]
        )


flash_deals_view = FlashDealsListAPIView.as_view()


@extend_schema_view(
    post=extend_schema(
        tags=["Products"],
        operation_id="Rate Product",
        request=ProductRatingSerializer,
        responses={201: ProductRatingSerializer},
    )
)
class RateProductAPIView(APIView):
    """Create or update the current user's 1–5 star rating for a product."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [ProductThrottling]

    def post(self, request, product_slug, *args, **kwargs):
        product = get_object_or_404(
            Product, product_slug=product_slug, active=True
        )

        if product.product_user_id == request.user.id:
            return Response(
                {"detail": "You cannot rate your own listing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProductRatingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rating, _ = ProductRating.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={"value": serializer.validated_data["value"]},
        )

        return Response(
            ProductRatingSerializer(rating).data,
            status=status.HTTP_201_CREATED,
        )


rate_product_view = RateProductAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Categories")
)
class CategoriesListAPIView(ListAPIView):
    queryset = with_category_context(Category.objects.all()).order_by("-created_at")
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    throttle_classes = [ProductThrottling]

    @cached_read_list(CATEGORY_LIST_CACHE)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

categories_list_view = CategoriesListAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Product Detail"),
    put=extend_schema(tags=["Products"], operation_id="Replace Product"),
    patch=extend_schema(tags=["Products"], operation_id="Update Product"),
    delete=extend_schema(tags=["Products"], operation_id="Delete Product"),
)
class ProductsDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly | IsAdminUser]
    throttle_classes = [ProductThrottling]
    lookup_field = "product_slug"
    lookup_url_kwarg = "product_slug"

    def get_queryset(self):
        return (
            with_rating_aggregates(with_listing_context(Product.objects.all()))
            .order_by("-created_at")
        )

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        # Track view: only if authenticated and NOT the owner
        if (
            request.user.is_authenticated
            and request.user.id != obj.product_user_id
            and not obj.views.filter(id=request.user.id).exists()
        ):
            obj.views.add(request.user)

        return self.retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        if serializer.validated_data.get("sold") is True:
            serializer.save(active=False)
        else:
            serializer.save()


products_detail_view = ProductsDetailAPIView.as_view()


# =============================================================================
# AUTHENTICATED
# =============================================================================

@extend_schema_view(
    post=extend_schema(tags=["Products"], operation_id="Create Product")
)
class CreateProductAPIView(CreateAPIView):
    serializer_class = ProductSerializer
    throttle_classes = [CreateProductThrottling]

    def perform_create(self, serializer):
        serializer.save(
            product_user=self.request.user,
            expires_at=timezone.now() + timedelta(days=30),
        )

create_product_view = CreateProductAPIView.as_view()


@extend_schema_view(
    post=extend_schema(tags=["Products"], operation_id="Upload Product Images")
)
class ProductImageCreateAPIView(CreateAPIView):
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product")
        images = request.FILES.getlist("images")
        # Direct-to-storage uploads attach by object key (see media_uploads).
        keys = request.data.getlist("keys") if hasattr(request.data, "getlist") else []
        if not keys and request.data.get("key"):
            keys = [request.data.get("key")]

        if not product_id:
            return Response(
                {"product": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not images and not keys:
            return Response(
                {"images": ["At least one image is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify product exists and belongs to the current user
        product = get_object_or_404(Product, id=product_id)
        if product.product_user.id != request.user.id:
            return Response(
                {"detail": "You can only upload images to your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )

        created = []
        for image in images:
            serializer = self.get_serializer(
                data={"product": product.id, "image": image}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            created.append(serializer.data)

        for image_key in keys:
            serializer = self.get_serializer(
                data={"product": product.id, "image_key": image_key}
            )
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
            if not obj.image:
                obj.delete()
                return Response(
                    {"image_key": ["The referenced upload is missing or invalid."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            created.append(serializer.data)

        return Response(created, status=status.HTTP_201_CREATED)

create_product_images_view = ProductImageCreateAPIView.as_view()


# =============================================================================
# MY LISTINGS
# =============================================================================

@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="My Listings")
)
class MyProductsListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ProductThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        queryset = with_listing_context(
            Product.objects.filter(product_user=self.request.user)
        )

        status_filter = (self.request.query_params.get("status") or "").lower()
        now = timezone.now()

        if status_filter == "sold":
            queryset = queryset.filter(sold=True)
        elif status_filter == "inactive":
            queryset = queryset.filter(sold=False, active=False)
        elif status_filter == "expired":
            queryset = queryset.filter(
                sold=False, active=True, expires_at__lte=now
            )
        elif status_filter == "active":
            queryset = queryset.filter(sold=False, active=True).exclude(
                expires_at__lte=now
            )

        return queryset.order_by("-created_at")


my_products_view = MyProductsListAPIView.as_view()


# =============================================================================
# FAVORITES & RECENTLY VIEWED
# =============================================================================

@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Favorite Products")
)
class FavoriteProductsListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ProductThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            with_listing_context(
                self.request.user.favorite_products.filter(active=True, sold=False)
            )
            .order_by("-created_at")
        )


favorite_products_view = FavoriteProductsListAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Recently Viewed Products")
)
class RecentlyViewedProductsListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ProductThrottling]
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            with_listing_context(
                self.request.user.viewed_products.filter(active=True, sold=False)
            )
            .order_by("-created_at")
        )


recently_viewed_products_view = RecentlyViewedProductsListAPIView.as_view()


# =============================================================================
# REPORT ABUSE
# =============================================================================

@extend_schema_view(
    post=extend_schema(
        tags=["Products"],
        operation_id="Report Product",
        request=ProductReportSerializer,
        responses={201: ProductReportSerializer},
    )
)
class ReportProductAPIView(CreateAPIView):
    serializer_class = ProductReportSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReportThrottling]

    def post(self, request, product_slug, *args, **kwargs):
        product = get_object_or_404(
            Product, product_slug=product_slug, active=True
        )

        serializer = self.get_serializer(
            data=request.data,
            context={"request": request, "product": product},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(product=product, reporter=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


report_product_view = ReportProductAPIView.as_view()


# =============================================================================
# IMAGE UPDATE / DELETE
# =============================================================================

@extend_schema_view(
    post=extend_schema(tags=["Products"], operation_id="Replace Product Images")
)
class ProductImageUpdateAPIView(APIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @transaction.atomic
    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        if product.product_user_id != request.user.id:
            return Response(
                {"detail": "You can only update images for your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )

        images = request.FILES.getlist("images")
        if not images:
            return Response(
                {"images": ["At least one image is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated = []
        for image in images:
            serializer = ProductImageSerializer(
                data={"product": product.id, "image": image},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            validated.append(serializer)

        # Replace the existing gallery once every new file has validated.
        ProductImage.objects.filter(product=product).delete()
        created = [serializer.save() for serializer in validated]

        output = ProductImageSerializer(
            created, many=True, context={"request": request}
        )
        return Response(output.data, status=status.HTTP_200_OK)


update_product_images_view = ProductImageUpdateAPIView.as_view()


@extend_schema_view(
    post=extend_schema(tags=["Products"], operation_id="Delete Product Image")
)
class ProductImageDeleteAPIView(APIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, image_id, *args, **kwargs):
        image = get_object_or_404(ProductImage, id=image_id)

        if image.product.product_user_id != request.user.id:
            return Response(
                {"detail": "You can only delete images from your own products."},
                status=status.HTTP_403_FORBIDDEN,
            )

        image.delete()

        return Response(
            {"detail": "Image deleted successfully."},
            status=status.HTTP_200_OK,
        )


delete_product_image_view = ProductImageDeleteAPIView.as_view()
