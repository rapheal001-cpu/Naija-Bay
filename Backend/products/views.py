from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status
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
)
from .models import Product, ProductImage, ProductReport
from core.models import Category
from NaijaBay.pagination import StandardPagination
from NaijaBay.permissions import IsOwnerOrReadOnly, IsOwnerOnly
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
    ]

    def get_queryset(self):
        now = timezone.now()
        return (
            Product.objects.filter(active=True, sold=False)
            .filter(Q(expires_at__isnull=True) | Q(expires_at__gt=now))
            .select_related("product_user")
            .prefetch_related("views", "favorites", "images")
            .order_by("-created_at")
        )

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        sort = (self.request.query_params.get("sort") or "").lower()

        if sort == "price_asc":
            return queryset.order_by("-promoted", "price", "-created_at")
        if sort == "price_desc":
            return queryset.order_by("-promoted", "-price", "-created_at")
        if sort == "oldest":
            return queryset.order_by("-promoted", "created_at")
        if sort in ("popular", "views"):
            return queryset.annotate(
                _views_total=Count("views", distinct=True)
            ).order_by("-promoted", "-_views_total", "-created_at")
        if sort == "favorites":
            return queryset.annotate(
                _favorites_total=Count("favorites", distinct=True)
            ).order_by("-promoted", "-_favorites_total", "-created_at")

        # Default: promoted listings first, then newest.
        return queryset.order_by("-promoted", "-created_at")


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
            Product.objects.filter(
                active=True,
                sold=False,
            )
            .select_related("product_user")
            .prefetch_related("views", "favorites", "images")
            .order_by("-created_at")[:50]
        )

featured_products_view = FeaturedProductsListAPIView.as_view()


@extend_schema_view(
    get=extend_schema(tags=["Products"], operation_id="Categories")
)
class CategoriesListAPIView(ListAPIView):
    queryset = Category.objects.prefetch_related("sub_categories").order_by(
        "-created_at"
    )
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    throttle_classes = [ProductThrottling]

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
            Product.objects.select_related("product_user")
            .prefetch_related("views", "favorites", "images")
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

        if not product_id:
            return Response(
                {"product": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not images:
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
        queryset = (
            Product.objects.filter(product_user=self.request.user)
            .select_related("product_user")
            .prefetch_related("views", "favorites", "images")
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
            self.request.user.favorite_products.filter(active=True, sold=False)
            .select_related("product_user")
            .prefetch_related("views", "favorites", "images")
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
            self.request.user.viewed_products.filter(active=True, sold=False)
            .select_related("product_user")
            .prefetch_related("views", "favorites", "images")
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
