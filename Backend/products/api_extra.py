"""Extra Jiji-style product APIs: offers, callback requests, ad videos."""

from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from NaijaBay.pagination import StandardPagination
from .models import Product, Offer, CallbackRequest, ProductVideo


class OfferSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source="buyer.username", read_only=True)
    product_name = serializers.CharField(source="product.product_name", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id", "product", "product_name", "buyer", "buyer_username",
            "amount", "message", "status", "expires_at", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "product", "buyer", "status", "expires_at", "created_at", "updated_at",
        ]


@extend_schema_view(get=extend_schema(tags=["Offers"]), post=extend_schema(tags=["Offers"]))
class ProductOffersAPIView(ListAPIView, CreateAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_product(self):
        return get_object_or_404(Product, product_slug=self.kwargs["product_slug"])

    def get_queryset(self):
        product = self.get_product()
        if product.product_user_id != self.request.user.id:
            return Offer.objects.none()
        return Offer.objects.filter(product=product).select_related("buyer", "product").order_by("-created_at")

    def perform_create(self, serializer):
        from django.utils import timezone
        from datetime import timedelta
        serializer.save(
            product=self.get_product(),
            buyer=self.request.user,
            status="pending",
            expires_at=timezone.now() + timedelta(days=7),
        )


@extend_schema_view(post=extend_schema(tags=["Offers"], operation_id="Respond to an offer"))
class OfferRespondAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        offer = get_object_or_404(Offer, pk=pk, product__product_user=request.user)
        action = request.data.get("action")
        if action not in ("accept", "decline"):
            return Response({"detail": "action must be 'accept' or 'decline'."}, status=status.HTTP_400_BAD_REQUEST)
        offer.status = "accepted" if action == "accept" else "declined"
        offer.save(update_fields=["status", "updated_at"])
        return Response(OfferSerializer(offer).data)


class CallbackRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallbackRequest
        fields = ["id", "product", "user", "phone", "status", "created_at"]
        read_only_fields = ["id", "product", "user", "status", "created_at"]


@extend_schema_view(post=extend_schema(tags=["Callbacks"], operation_id="Request a call back"))
class CallbackCreateAPIView(CreateAPIView):
    serializer_class = CallbackRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            product=get_object_or_404(Product, product_slug=self.kwargs["product_slug"]),
            user=self.request.user,
            status="pending",
        )


class ProductVideoSerializer(serializers.ModelSerializer):
    video_key = serializers.CharField(write_only=True, required=False, max_length=512)

    class Meta:
        model = ProductVideo
        fields = ["id", "product", "video", "video_key", "title", "created_at"]
        read_only_fields = ["id", "product", "created_at"]

    def validate(self, attrs):
        from django.core.files.storage import default_storage
        from NaijaBay.direct_uploads import is_own_direct_upload_key

        key = attrs.get("video_key")
        if not attrs.get("video") and not key:
            raise serializers.ValidationError({"video": "Provide a file or a video_key."})
        if key:
            user_id = getattr(getattr(self.context.get("request"), "user", None), "pk", None)
            key = key.strip()
            if not is_own_direct_upload_key(key, user_id, purpose="ad-video"):
                raise serializers.ValidationError({"video_key": "This file was not uploaded by you."})
            try:
                if not default_storage.exists(key):
                    raise serializers.ValidationError(
                        {"video_key": "The uploaded file was not found. Please upload it again."}
                    )
            except serializers.ValidationError:
                raise
            except Exception:
                pass
            attrs["video_key"] = key
        return attrs


@extend_schema_view(get=extend_schema(tags=["Videos"]))
class ProductVideoListAPIView(ListAPIView):
    serializer_class = ProductVideoSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return ProductVideo.objects.filter(product__product_slug=self.kwargs["product_slug"]).order_by("created_at")


@extend_schema_view(post=extend_schema(tags=["Videos"], operation_id="Upload ad video"))
class ProductVideoUploadAPIView(CreateAPIView):
    serializer_class = ProductVideoSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        product = get_object_or_404(
            Product, product_slug=self.kwargs["product_slug"], product_user=self.request.user
        )
        key = serializer.validated_data.pop("video_key", None)
        serializer.save(product=product, **({"video": key} if key else {}))
