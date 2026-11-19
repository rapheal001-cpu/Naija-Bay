"""Extra Jiji-style account APIs: seller feedback, saved searches, Verified ID."""

from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from NaijaBay.pagination import StandardPagination
from .models import SellerFeedback, SavedSearch, VerificationRequest


# ---------------------------------------------------------------------------
# SELLER FEEDBACK
# ---------------------------------------------------------------------------

class SellerFeedbackSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source="seller.username", read_only=True)
    author_username = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = SellerFeedback
        fields = [
            "id", "seller", "seller_username", "author", "author_username",
            "rating", "comment", "status", "response", "appeal", "edited",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "author", "status", "response", "appeal", "edited",
            "created_at", "updated_at",
        ]


@extend_schema_view(get=extend_schema(tags=["Feedback"], operation_id="List seller feedback"))
class SellerFeedbackListAPIView(ListAPIView):
    serializer_class = SellerFeedbackSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination

    def get_queryset(self):
        qs = SellerFeedback.objects.filter(status="approved").select_related("seller", "author")
        seller = self.request.query_params.get("seller")
        if seller:
            qs = qs.filter(seller_id=seller)
        return qs.order_by("-created_at")


@extend_schema_view(post=extend_schema(tags=["Feedback"], operation_id="Leave seller feedback"))
class SellerFeedbackCreateAPIView(CreateAPIView):
    serializer_class = SellerFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, status="pending")


@extend_schema_view(
    patch=extend_schema(tags=["Feedback"], operation_id="Edit feedback"),
    delete=extend_schema(tags=["Feedback"], operation_id="Delete feedback"),
)
class SellerFeedbackDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = SellerFeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SellerFeedback.objects.filter(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(edited=True, status="pending")


@extend_schema_view(post=extend_schema(tags=["Feedback"], operation_id="Appeal feedback"))
class FeedbackAppealAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            fb = SellerFeedback.objects.get(pk=pk, seller=request.user)
        except SellerFeedback.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        fb.appeal = request.data.get("appeal", "")
        fb.save(update_fields=["appeal", "updated_at"])
        return Response(SellerFeedbackSerializer(fb).data)


@extend_schema_view(post=extend_schema(tags=["Feedback"], operation_id="Respond to feedback"))
class FeedbackResponseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            fb = SellerFeedback.objects.get(pk=pk, seller=request.user)
        except SellerFeedback.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        fb.response = request.data.get("response", "")
        fb.save(update_fields=["response", "updated_at"])
        return Response(SellerFeedbackSerializer(fb).data)


# ---------------------------------------------------------------------------
# SAVED SEARCHES
# ---------------------------------------------------------------------------

class SavedSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedSearch
        fields = ["id", "name", "query_params", "notify", "created_at"]
        read_only_fields = ["id", "created_at"]


@extend_schema_view(get=extend_schema(tags=["Saved searches"]), post=extend_schema(tags=["Saved searches"]))
class SavedSearchListCreateAPIView(ListAPIView, CreateAPIView):
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema_view(
    patch=extend_schema(tags=["Saved searches"]),
    delete=extend_schema(tags=["Saved searches"]),
)
class SavedSearchDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = SavedSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedSearch.objects.filter(user=self.request.user)


# ---------------------------------------------------------------------------
# VERIFIED ID (KYC)
# ---------------------------------------------------------------------------

class VerificationRequestSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    selfie_key = serializers.CharField(write_only=True, required=False, max_length=512)
    document_key = serializers.CharField(write_only=True, required=False, max_length=512)

    class Meta:
        model = VerificationRequest
        fields = [
            "id", "id_type", "id_number", "selfie", "document",
            "selfie_key", "document_key", "status",
            "status_display", "reviewer_note", "reviewed_at", "created_at",
        ]
        read_only_fields = [
            "id", "status", "status_display", "reviewer_note", "reviewed_at", "created_at",
        ]

    def validate(self, attrs):
        from NaijaBay.direct_uploads import is_own_direct_upload_key

        user_id = getattr(getattr(self.context.get("request"), "user", None), "pk", None)
        for field, purpose in (("selfie_key", "verification-selfie"), ("document_key", "verification-document")):
            key = attrs.get(field)
            if key and not is_own_direct_upload_key(key.strip(), user_id, purpose=purpose):
                raise serializers.ValidationError({field: "This file was not uploaded by you."})
            if key:
                attrs[field] = key.strip()
        return attrs


@extend_schema_view(post=extend_schema(tags=["Verification"], operation_id="Submit Verified ID"))
class VerificationRequestCreateAPIView(CreateAPIView):
    serializer_class = VerificationRequestSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        data = dict(serializer.validated_data)
        selfie_key = data.pop("selfie_key", None)
        document_key = data.pop("document_key", None)
        if selfie_key:
            data["selfie"] = selfie_key
        if document_key:
            data["document"] = document_key
        serializer.save(user=self.request.user, status="pending", **data)


@extend_schema_view(get=extend_schema(tags=["Verification"], operation_id="My verification status"))
class MyVerificationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = VerificationRequest.objects.filter(user=request.user).order_by("-created_at").first()
        if not item:
            return Response({"status": "none", "verified": bool(request.user.verified)})
        return Response({
            **VerificationRequestSerializer(item).data,
            "verified": bool(request.user.verified),
        })
