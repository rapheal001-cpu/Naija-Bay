from django.db import transaction
from rest_framework import status
from rest_framework.generics import (
    get_object_or_404,
    ListAPIView,
    CreateAPIView,
    UpdateAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView,
)
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from .serializers import ProductImageSerializer, ProductSerializer, CategorySerializer
from .models import Product, ProductImage
from core.models import Category
from NaijaBay.permissions import IsOwnerOrReadOnly, IsOwnerOnly
from NaijaBay.throttling import ProductThrottling, CreateProductThrottling


# =============================================================================
# GENERAL
# =============================================================================

@extend_schema_view(get=extend_schema(tags=["Products"], operation_id="Products"))
class ProductsListAPIView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ProductThrottling]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = [
        "product_name",
        "description",
        "category",
        "sub_category",
        "condition",
        "state",
        "city",
    ]
    filterset_fields = ["category", "sub_category"]

    def get_queryset(self):
        return (
            Product.objects.filter(active=True, sold=False)
            .select_related("product_user")
            .prefetch_related("views", "favorites", "images")
            .order_by("-product_user__verified", "-created_at")
        )

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
                product_user__verified=True,
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
    put=extend_schema(tags=["Products"], operation_id="Update Product"),
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
        serializer.save(product_user=self.request.user)

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


@extend_schema_view(
    post=extend_schema(tags=["Products"], operation_id="Update Product Images")
)
class UpdateProductImageCreateAPIView(UpdateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsOwnerOnly | IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

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

update_product_images_view = UpdateProductImageCreateAPIView.as_view()


@extend_schema_view(
    delete=extend_schema(tags=["Products"], operation_id="Delete Product Image")
)
class DeleteProductImageAPIView(DestroyAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [IsOwnerOnly | IsAdminUser]
    queryset = ProductImage.objects.select_related('product')
    lookup_field = 'pk'
    lookup_url_kwarg = 'pk'

    def delete(self, request, *args, **kwargs):
        image = get_object_or_404(ProductImage, pk=kwargs.get('pk'))
        if image.product.product_user.id != request.user.id:
            return Response(
                {"detail": "You can only delete your own product images."},
                status=status.HTTP_403_FORBIDDEN,
            )
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

delete_product_image_view = DeleteProductImageAPIView.as_view()
