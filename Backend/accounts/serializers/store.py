from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from accounts.models import Store, User
from products.models import Product
from NaijaBay.utils import FILE_UPLOAD_ALLOWED_EXTENSIONS, STATE_CHOICES


# =============================================================================
# SHARED COMPACT USER
# =============================================================================

class StoreOwnerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    followers_count = serializers.SerializerMethodField()
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "full_name",
            "avatar",
            "verified",
            "state",
            "date_joined",
            "followers_count",
            "products_count",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_followers_count(self, obj):
        return obj.followers_count

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_products_count(self, obj):
        return obj.products.filter(active=True, sold=False).count()


class FollowUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "full_name", "avatar", "verified", "date_joined"]
        read_only_fields = fields


# =============================================================================
# STORE
# =============================================================================

class StoreSerializer(serializers.ModelSerializer):
    owner = StoreOwnerSerializer(read_only=True, source="user")
    products_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "logo",
            "banner",
            "verified",
            "state",
            "address",
            "owner",
            "products_count",
            "followers_count",
            "is_following",
            "is_owner",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "slug",
            "verified",
            "owner",
            "products_count",
            "followers_count",
            "is_following",
            "is_owner",
            "created_at",
            "updated_at",
        )

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_products_count(self, obj):
        return obj.products_count

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_followers_count(self, obj):
        return obj.user.followers.count()

    @extend_schema_field(serializers.BooleanField(default=False))
    def get_is_following(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.user.followers.filter(follower=request.user).exists()

    @extend_schema_field(serializers.BooleanField(default=False))
    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.user_id == request.user.id
        )


class StoreDetailSerializer(StoreSerializer):
    products = serializers.SerializerMethodField()

    class Meta(StoreSerializer.Meta):
        fields = StoreSerializer.Meta.fields + ["products"]

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_products(self, obj):
        # Imported lazily to avoid a circular import at module load time.
        from products.serializers import ProductSerializer

        products = (
            Product.objects.filter(product_user=obj.user, active=True, sold=False)
            .select_related("product_user")
            .prefetch_related("images", "views", "favorites")
            .order_by("-created_at")[:60]
        )
        return ProductSerializer(products, many=True, context=self.context).data


class StoreCreateSerializer(serializers.ModelSerializer):
    """Create or update the store owned by the authenticated user."""

    class Meta:
        model = Store
        fields = [
            "name",
            "description",
            "logo",
            "banner",
            "state",
            "address",
        ]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Store name must be at least 3 characters."
            )
        if len(value) > 60:
            raise serializers.ValidationError(
                "Store name must be at most 60 characters."
            )

        existing = Store.objects.filter(name__iexact=value)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise serializers.ValidationError("A store with this name already exists.")
        return value

    def validate_state(self, value):
        if value:
            valid = [choice[0] for choice in STATE_CHOICES]
            if value not in valid:
                raise serializers.ValidationError("Invalid state.")
        return value

    def _validate_image(self, image, label):
        if not image:
            return image
        name = image.name.lower()
        if not name.endswith(tuple(FILE_UPLOAD_ALLOWED_EXTENSIONS)):
            raise serializers.ValidationError(
                f"{label} format is not supported. Allowed: "
                f"{', '.join(FILE_UPLOAD_ALLOWED_EXTENSIONS)}."
            )
        if image.size > 2 * 1024 * 1024:
            raise serializers.ValidationError(f"{label} must be smaller than 2MB.")
        return image

    def validate_logo(self, value):
        return self._validate_image(value, "Logo")

    def validate_banner(self, value):
        return self._validate_image(value, "Banner")
