from decimal import Decimal
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from accounts.models import User
from core.models import Category, SubCategory, State, City
from .models import Product, ProductImage
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
    class Meta:
        model = User
        fields = ['id', 'avatar', 'full_name', 'username', 'is_active', 'verified', 'date_joined']

class ProductSerializer(serializers.ModelSerializer):
    product_user = ProductUserSerializer(read_only=True)
    color = serializers.CharField(style={"input_type": "color"})
    price = serializers.DecimalField(decimal_places=2,max_digits=15, min_value=Decimal("1000.00"),max_value=Decimal("999999999.99"))
    quantity = serializers.IntegerField(default=1)
    negotiable = serializers.BooleanField(default=False)
    sold = serializers.BooleanField(default=False)
    state = serializers.ChoiceField(choices=STATE_CHOICES)
    city = serializers.ChoiceField(choices=CITY_CHOICES)
    category = serializers.ChoiceField(choices=CATEGORY_CHOICES)
    sub_category = serializers.ChoiceField(choices=SUBCATEGORY_CHOICES)
    contact_methods = serializers.ListField(child=serializers.ChoiceField(choices=CONTACT_METHOD_CHOICES))
    contact_number = PhoneNumberField()
    images = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    favorites_count = serializers.SerializerMethodField(read_only=True)
    views_count = serializers.SerializerMethodField(read_only=True)
    images_count = serializers.SerializerMethodField(read_only=True)

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
        if not Category.objects.filter(slug=_normalize(value)).exists():
            raise serializers.ValidationError(
                "This category does not exist in our database."
            )
        return value

    def validate_sub_category(self, value):
        if not SubCategory.objects.filter(slug=_normalize(value)).exists():
            raise serializers.ValidationError("This sub category is not valid.")
        return value

    def validate_state(self, value):
        if not State.objects.filter(slug=_normalize(value)).exists():
            raise serializers.ValidationError("Invalid state.")
        return value

    def validate_city(self, value):
        if not City.objects.filter(slug=_normalize(value)).exists():
            raise serializers.ValidationError("Invalid city.")
        return value

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
