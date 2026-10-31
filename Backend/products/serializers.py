from decimal import Decimal
from django.db import models
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from accounts.models import User
from core.models import Category, SubCategory, State, City
from .models import Product, ProductImage, ProductReport, ProductRating
from phonenumber_field.serializerfields import PhoneNumberField
from NaijaBay.utils import (
    CONTACT_METHOD_CHOICES,
    FILE_UPLOAD_ALLOWED_EXTENSIONS,
    STATE_CHOICES,
    CITY_CHOICES,
    CATEGORY_CHOICES,
    SUBCATEGORY_CHOICES,
    _normalize,
)

# =============================================================================
# PRODUCT SERIALIZER
# =============================================================================

class ProductUserSerializer(serializers.ModelSerializer):
    store = serializers.SerializerMethodField(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'avatar',
            'full_name',
            'username',
            'is_active',
            'verified',
            'store',
            'date_joined',
        ]

    @extend_schema_field(
        serializers.DictField(child=serializers.CharField(), allow_null=True)
    )
    def get_store(self, obj):
        store = getattr(obj, "store", None)
        if not store:
            return None
        return {
            "name": store.name,
            "slug": store.slug,
            "verified": store.verified,
        }

class ProductSerializer(serializers.ModelSerializer):
    product_user = ProductUserSerializer(read_only=True)
    color = serializers.CharField(style={"input_type": "color"})
    price = serializers.DecimalField(decimal_places=2,max_digits=15, min_value=Decimal("1000.00"),max_value=Decimal("999999999.99"))
    quantity = serializers.IntegerField(default=1)
    negotiable = serializers.BooleanField(default=False)
    sold = serializers.BooleanField(default=False)
    state = serializers.CharField()
    city = serializers.CharField()
    category = serializers.CharField()
    sub_category = serializers.CharField()
    contact_methods = serializers.ListField(child=serializers.ChoiceField(choices=CONTACT_METHOD_CHOICES))
    contact_number = PhoneNumberField()
    images = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    favorites_count = serializers.SerializerMethodField(read_only=True)
    views_count = serializers.SerializerMethodField(read_only=True)
    images_count = serializers.SerializerMethodField(read_only=True)
    listing_status = serializers.CharField(read_only=True)
    is_owner = serializers.SerializerMethodField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    total_ratings = serializers.SerializerMethodField(read_only=True)
    user_rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "product_user",
            "product_name",
            "product_slug",
            "description",
            "price",
            "category",
            "sub_category",
            "condition",
            "color",
            "quantity",
            "negotiable",
            "original_price",
            "sold_count",
            "discount_percent",
            "average_rating",
            "total_ratings",
            "user_rating",
            "state",
            "city",
            "contact_methods",
            "contact_number",
            "images",
            "favorites_count",
            "views_count",
            "images_count",
            "active",
            "sold",
            "promoted",
            "delivery_available",
            "expires_at",
            "listing_status",
            "is_owner",
            "created_at",
            "updated_at",
            "is_favorited",
        ]
        read_only_fields = (
            "product_user",
            "product_slug",
            "views",
            "favorites",
            "active",
            "promoted",
            "created_at",
            "updated_at",
        )

    # -------------------------------------------------------------------------
    # Read-only computed fields
    # -------------------------------------------------------------------------

    @extend_schema_field(serializers.BooleanField(default=False))
    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.favorites.filter(id=request.user.id).exists()

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_favorites_count(self, obj):
        return obj.favorites_count

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_views_count(self, obj):
        return obj.views_count

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_images_count(self, obj):
        return obj.images_count

    @extend_schema_field(serializers.FloatField(default=0))
    def get_average_rating(self, obj):
        avg = getattr(obj, "_average_rating", None)
        if avg is not None:
            return round(float(avg), 1)
        return round(float(obj.ratings.aggregate(avg=models.Avg("value"))["avg"] or 0), 1)

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_total_ratings(self, obj):
        total = getattr(obj, "_total_ratings", None)
        if total is not None:
            return int(total)
        return obj.ratings.count()

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_user_rating(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        rating = obj.ratings.filter(user_id=request.user.id).first()
        return rating.value if rating else None

    @extend_schema_field(serializers.BooleanField(default=False))
    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.product_user_id == request.user.id
        )

    @extend_schema_field(serializers.ListField(child=serializers.CharField()))
    def get_images(self, obj):
        request = self.context.get("request")
        if request:
            return [
                request.build_absolute_uri(img.image.url) for img in obj.images.all()
            ]
        return [img.image.url for img in obj.images.all()]

    # -------------------------------------------------------------------------
    # Field validators
    # -------------------------------------------------------------------------

    def validate_product_name(self, value):
        value = value.strip().title()
        if len(value) < 3:
            raise serializers.ValidationError(
                "Product name must be at least 3 characters."
            )
        return value

    def validate_description(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError(
                "Description must be at least 20 characters."
            )
        return value

    def validate_category(self, value):
        normalized = _normalize(value)
        if not Category.objects.filter(slug=normalized).exists():
            raise serializers.ValidationError(
                "This category does not exist in our database."
            )
        # Store the canonical choice key (e.g. ``phones_tablets``) even when
        # the client sends the hyphenated public slug (``phones-tablets``).
        return normalized.replace("-", "_")

    def validate_sub_category(self, value):
        normalized = _normalize(value)
        if not SubCategory.objects.filter(slug=normalized).exists():
            raise serializers.ValidationError("This sub category is not valid.")
        return normalized.replace("-", "_")

    def validate_state(self, value):
        normalized = _normalize(value)
        if not State.objects.filter(slug=normalized).exists():
            raise serializers.ValidationError("Invalid state.")
        return normalized.replace("-", "_")

    def validate_city(self, value):
        normalized = _normalize(value)
        if not City.objects.filter(slug=normalized).exists():
            raise serializers.ValidationError("Invalid city.")
        return normalized.replace("-", "_")

    def validate_color(self, value):
        if not value:
            raise serializers.ValidationError("Select a color for your product.")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        if value > 10000:
            raise serializers.ValidationError(
                "Quantity seems too high. Contact support for bulk products."
            )
        return value

    def validate_contact_methods(self, value):
        if not value:
            raise serializers.ValidationError("Select at least one contact method.")

        valid = [choice[0] for choice in CONTACT_METHOD_CHOICES]
        if not isinstance(value, list):
            raise serializers.ValidationError("Contact methods must be a list.")

        for method in value:
            if method not in valid:
                raise serializers.ValidationError(
                    f"Invalid contact method '{method}'. Choose from: {', '.join(valid)}"
                )

        return list(dict.fromkeys(value))

    def validate_contact_number(self, value):
        if not value:
            return value

        cleaned = str(value).replace("+234", "0").replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise serializers.ValidationError(
                "Contact number must contain only digits."
            )
        if len(cleaned) != 11:
            raise serializers.ValidationError(
                "Contact number must be exactly 11 digits (e.g. 09012345678)."
            )
        return cleaned

    # -------------------------------------------------------------------------
    # Object-level validation
    # -------------------------------------------------------------------------

    def validate(self, attrs):
        category = attrs.get("category", getattr(self.instance, 'category', ''))
        sub_category = attrs.get("sub_category", getattr(self.instance, 'sub_category', ''))

        # Category ↔ SubCategory relationship
        if category and sub_category:
            try:
                cat = Category.objects.get(slug=_normalize(category))
                if not SubCategory.objects.filter(
                    category=cat, slug=_normalize(sub_category)
                ).exists():
                    raise serializers.ValidationError({"sub_category": f"'{sub_category}' does not belong to category '{cat.name}'."})

            except Category.DoesNotExist:
                raise serializers.ValidationError({"category": f"{category} does not exist."})

        state = attrs.get("state", getattr(self.instance, 'state', ''))
        city = attrs.get("city", getattr(self.instance, 'city', ''))

        # State ↔ City relationship
        if state and city:
            try:
                st = State.objects.get(slug=_normalize(state))
                if not City.objects.filter(state=st, slug=_normalize(city)).exists():
                    raise serializers.ValidationError({"city": f"'{city}' does not belong to state '{st.name}'."})

            except State.DoesNotExist:
                raise serializers.ValidationError({"state": f"{state} does not exist."})

        # Contact methods ↔ Contact number relationship
        contact_methods = attrs.get("contact_methods", getattr(self.instance, 'contact_methods', []))
        contact_number = attrs.get("contact_number", getattr(self.instance, 'contact_number', ''))

        needs_phone = any(m in contact_methods for m in ("phone_call", "whatsapp"))

        if needs_phone and not contact_number:
            raise serializers.ValidationError({"contact_number": "Contact number is required when Phone Call or WhatsApp is selected."})

        price = attrs.get("price", getattr(self.instance, "price", None))
        original_price = attrs.get(
            "original_price", getattr(self.instance, "original_price", None)
        )
        if original_price and price and original_price <= price:
            raise serializers.ValidationError(
                {"original_price": "Original price must be higher than the sale price to show a discount."}
            )

        return attrs

    # -------------------------------------------------------------------------
    # Create / Update
    # -------------------------------------------------------------------------

    def create(self, validated_data):
        product = Product.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


# =============================================================================
# PRODUCT IMAGE SERIALIZER
# =============================================================================

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "created_at"]
        read_only_fields = ("id", "created_at")

    def validate_image(self, image):
        name = image.name.lower()
        size = image.size

        if not name.endswith(tuple(FILE_UPLOAD_ALLOWED_EXTENSIONS)):
            allowed = ", ".join(FILE_UPLOAD_ALLOWED_EXTENSIONS)
            raise serializers.ValidationError(
                f"Format not accepted. Allowed: {allowed}"
            )

        if size > 2 * 1024 * 1024:
            mb = size / (1024 * 1024)
            raise serializers.ValidationError(
                f"Max image size is 2MB. This file is {mb:.1f}MB"
            )

        return image

    def create(self, validated_data):
        product_image = ProductImage.objects.create(**validated_data)
        return product_image

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        return instance


# =============================================================================
# CATEGORY SERIALIZER
# =============================================================================

class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "sub_categories", "created_at"]
        read_only_fields = fields

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_sub_categories(self, obj):
        return [
            {
                "slug": sub.slug,
                "name": sub.name,
            }
            for sub in obj.sub_categories.all()
        ]


# =============================================================================
# PRODUCT REPORT (ABUSE)
# =============================================================================

class ProductReportSerializer(serializers.ModelSerializer):
    reporter = ProductUserSerializer(read_only=True)

    class Meta:
        model = ProductReport
        fields = [
            "id",
            "product",
            "reporter",
            "reason",
            "details",
            "status",
            "created_at",
        ]
        read_only_fields = ("id", "product", "reporter", "status", "created_at")

    def validate_details(self, details):
        details = (details or "").strip()
        if details and len(details) > 2000:
            raise serializers.ValidationError(
                "Details are too long (maximum 2000 characters)."
            )
        return details

    def validate(self, attrs):
        request = self.context.get("request")
        product = self.context.get("product")

        if request and product:
            if product.product_user_id == request.user.id:
                raise serializers.ValidationError(
                    "You cannot report your own listing."
                )
            if ProductReport.objects.filter(
                product=product, reporter=request.user
            ).exists():
                raise serializers.ValidationError(
                    "You have already reported this listing."
                )
        return attrs


# =============================================================================
# PRODUCT RATING
# =============================================================================

class ProductRatingSerializer(serializers.ModelSerializer):
    user = ProductUserSerializer(read_only=True)

    class Meta:
        model = ProductRating
        fields = ["id", "product", "user", "value", "created_at"]
        read_only_fields = ("id", "user", "created_at")

    def validate_value(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


# =============================================================================
# SELLER / STORE SUMMARY
# =============================================================================

class ProductSellerSerializer(serializers.Serializer):
    """Lightweight seller payload used by the public seller profile page."""

    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField()
    avatar = serializers.CharField(allow_null=True)
    verified = serializers.BooleanField()
    state = serializers.CharField()
    bio = serializers.CharField(allow_blank=True)
    store = serializers.DictField(allow_null=True)
    products_count = serializers.IntegerField()
    followers_count = serializers.IntegerField()
    following_count = serializers.IntegerField()
    is_following = serializers.BooleanField()
