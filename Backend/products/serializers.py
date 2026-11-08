from decimal import Decimal
from django.db import models
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from accounts.models import User
import datetime
from decimal import Decimal
from django.db import transaction
from django.db.models import Q

from core.models import AttributeDefinition, Category, City, State, SubCategory
from .models import Product, ProductAttribute, ProductImage, ProductReport, ProductRating
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
    is_boosted = serializers.BooleanField(read_only=True)
    is_purchasable = serializers.BooleanField(read_only=True)
    is_owner = serializers.SerializerMethodField(read_only=True)
    discount_percent = serializers.IntegerField(read_only=True)
    average_rating = serializers.SerializerMethodField(read_only=True)
    total_ratings = serializers.SerializerMethodField(read_only=True)
    user_rating = serializers.SerializerMethodField(read_only=True)
    # Write: {'year': 2019, 'make': 'toyota'} — validated against the
    # category's AttributeDefinitions. Read: list of saved values.
    attributes = serializers.DictField(
        required=False,
        allow_null=True,
        help_text="Category-specific specifications keyed by attribute slug (e.g. {'year': 2019, 'make': 'toyota'}). Values are validated against GET /api/v1/core/attributes/?category=...&sub_category=.... Sending null clears an attribute on update.",
    )

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
            "promoted_until",
            "boost_level",
            "is_boosted",
            "is_purchasable",
            "delivery_available",
            "expires_at",
            "listing_status",
            "is_owner",
            "created_at",
            "updated_at",
            "is_favorited",
            "attributes",
        ]
        read_only_fields = (
            "product_user",
            "product_slug",
            "views",
            "favorites",
            "active",
            "promoted",
            "promoted_until",
            "boost_level",
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
        cached = getattr(obj, "prefetched_favorites", None)
        if cached is not None:
            return any(u.id == request.user.id for u in cached)
        cached = obj._prefetched_objects_cache.get("favorites") if hasattr(obj, "_prefetched_objects_cache") else None
        if cached is not None:
            return any(u.id == request.user.id for u in cached)
        return obj.favorites.filter(id=request.user.id).exists()

    def _cached_ratings(self, obj):
        cached = getattr(obj, "prefetched_ratings", None)
        if cached is not None:
            return cached
        if hasattr(obj, "_prefetched_objects_cache"):
            return obj._prefetched_objects_cache.get("ratings")
        return None

    def _cached_len(self, obj, relation, attr_name):
        """Length of a prefetched relation via its to_attr list, if present."""
        rows = getattr(obj, attr_name, None)
        if rows is not None:
            return len(rows)
        return None

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_favorites_count(self, obj):
        cached = self._cached_len(obj, "favorites", "prefetched_favorites")
        if cached is not None:
            return cached
        return obj.favorites_count

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_views_count(self, obj):
        cached = self._cached_len(obj, "views", "prefetched_views")
        if cached is not None:
            return cached
        return obj.views_count

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_images_count(self, obj):
        return obj.images_count

    @extend_schema_field(serializers.FloatField(default=0))
    def get_average_rating(self, obj):
        avg = getattr(obj, "_average_rating", None)
        if avg is not None:
            return round(float(avg), 1)
        cached = self._cached_ratings(obj)
        if cached is not None:
            if not cached:
                return 0.0
            return round(sum(r.value for r in cached) / len(cached), 1)
        return round(float(obj.ratings.aggregate(avg=models.Avg("value"))["avg"] or 0), 1)

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_total_ratings(self, obj):
        total = getattr(obj, "_total_ratings", None)
        if total is not None:
            return int(total)
        cached = self._cached_ratings(obj)
        if cached is not None:
            return len(cached)
        return obj.ratings.count()

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_user_rating(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        cached = self._cached_ratings(obj)
        if cached is not None:
            for rating in cached:
                if rating.user_id == request.user.id:
                    return rating.value
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
        cached = getattr(obj, "prefetched_images", None)
        images = cached if cached is not None else obj.images.all()
        if request:
            return [
                request.build_absolute_uri(img.image.url) for img in images
            ]
        return [img.image.url for img in images]

    # -------------------------------------------------------------------------
    # Category-specific attributes (write + read)
    # -------------------------------------------------------------------------

    def _definitions_scope(self, category_value, sub_category_value):
        """AttributeDefinitions for a category (category-wide + subcategory)."""
        category = None
        if category_value:
            normalized = _normalize(category_value).replace("_", "-")
            category = Category.objects.filter(slug=normalized).first()
        if category is None:
            return [], None, None

        sub_category = None
        if sub_category_value:
            normalized = _normalize(sub_category_value).replace("_", "-")
            sub_category = SubCategory.objects.filter(category=category, slug=normalized).first()

        qs = (
            AttributeDefinition.objects.filter(category=category)
            .prefetch_related("options")
        )
        if sub_category is not None:
            qs = qs.filter(Q(sub_category__isnull=True) | Q(sub_category=sub_category))
        else:
            qs = qs.filter(sub_category__isnull=True)
        return list(qs.order_by("sort_order", "name")), category, sub_category

    def _coerce_attribute_value(self, definition, raw):
        """Validate one submitted value against its definition.

        Returns ``{"value_text": ..., "value_number": ..., ...}`` kwargs, or raises
        a ValidationError keyed by the attribute slug.
        """
        dtype = definition.data_type

        if dtype in ("number", "decimal"):
            if isinstance(raw, bool) or not isinstance(raw, (int, float, str)):
                raise serializers.ValidationError(f"'{definition.label}' must be a number.")
            try:
                number = Decimal(str(raw))
            except Exception:
                raise serializers.ValidationError(f"'{definition.label}' must be a number.")
            if definition.min_value is not None and number < definition.min_value:
                raise serializers.ValidationError(f"'{definition.label}' is below the minimum of {definition.min_value:g}.")
            if definition.max_value is not None and number > definition.max_value:
                raise serializers.ValidationError(f"'{definition.label}' is above the maximum of {definition.max_value:g}.")
            return {"value_text": None, "value_number": number, "value_bool": None, "value_date": None, "value_list": None}

        if dtype == "boolean":
            if isinstance(raw, bool):
                value = raw
            elif isinstance(raw, str) and raw.lower() in ("true", "false"):
                value = raw.lower() == "true"
            else:
                raise serializers.ValidationError(f"'{definition.label}' must be true or false.")
            return {"value_text": None, "value_number": None, "value_bool": value, "value_date": None, "value_list": None}

        if dtype == "date":
            if not isinstance(raw, str):
                raise serializers.ValidationError(f"'{definition.label}' must be an ISO date (YYYY-MM-DD).")
            try:
                value = datetime.date.fromisoformat(raw)
            except ValueError:
                raise serializers.ValidationError(f"'{definition.label}' must be an ISO date (YYYY-MM-DD).")
            return {"value_text": None, "value_number": None, "value_bool": None, "value_date": value, "value_list": None}

        if dtype in ("select", "multiselect"):
            allowed = set(definition.options.values_list("value", flat=True))
            if dtype == "select":
                if raw not in allowed:
                    raise serializers.ValidationError(
                        f"'{definition.label}' must be one of: {', '.join(sorted(allowed)) or '—'}."
                    )
                return {"value_text": raw, "value_number": None, "value_bool": None, "value_date": None, "value_list": None}
            if not isinstance(raw, list):
                raise serializers.ValidationError(f"'{definition.label}' must be a list of options.")
            invalid = [v for v in raw if v not in allowed]
            if invalid:
                raise serializers.ValidationError(
                    f"'{definition.label}' has invalid option(s): {', '.join(str(v) for v in invalid)}."
                )
            return {"value_text": None, "value_number": None, "value_bool": None, "value_date": None, "value_list": list(raw)}

        # text
        text = str(raw).strip()
        if not text:
            raise serializers.ValidationError(f"'{definition.label}' cannot be empty.")
        return {"value_text": text, "value_number": None, "value_bool": None, "value_date": None, "value_list": None}

    def _validate_attributes(self, attrs):
        """Validate the optional ``attributes`` dict against the category scope."""
        attributes = attrs.get("attributes")
        if attributes is None:
            return attrs  # legacy payloads stay untouched

        category = attrs.get("category", getattr(self.instance, "category", ""))
        sub_category = attrs.get("sub_category", getattr(self.instance, "sub_category", ""))
        definitions, _, _ = self._definitions_scope(category, sub_category)
        by_slug = {d.slug: d for d in definitions}

        errors = {}
        for slug, raw in attributes.items():
            if raw is None:
                continue  # explicit clear (update path handles the delete)
            definition = by_slug.get(slug)
            if definition is None:
                errors[slug] = "Unknown attribute for this category."
                continue
            try:
                self._coerce_attribute_value(definition, raw)
            except serializers.ValidationError as exc:
                errors[slug] = exc.detail

        # Required definitions must be supplied whenever attributes are posted.
        for definition in definitions:
            if definition.required and attributes.get(definition.slug) in (None, "", []):
                errors[definition.slug] = f"'{definition.label}' is required for this category."

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def _save_attributes(self, product, attributes):
        """Upsert submitted attributes; ``None`` clears an attribute."""
        if attributes is None:
            return
        definitions, _, _ = self._definitions_scope(product.category, product.sub_category)
        by_slug = {d.slug: d for d in definitions}
        for slug, raw in attributes.items():
            if raw is None:
                ProductAttribute.objects.filter(product=product, definition__slug=slug).delete()
                continue
            definition = by_slug[slug]
            values = self._coerce_attribute_value(definition, raw)
            ProductAttribute.objects.update_or_create(
                product=product, definition=definition, defaults=values
            )

    def _resolve_fk_fields(self, attrs):
        """Keep the relational FKs in sync with the legacy string fields."""
        category = attrs.get("category")
        if category:
            normalized = _normalize(category).replace("_", "-")
            cat = Category.objects.filter(slug=normalized).first()
            if cat:
                attrs["category_obj"] = cat
                sub_value = attrs.get("sub_category")
                if sub_value:
                    sub = SubCategory.objects.filter(
                        category=cat, slug=_normalize(sub_value).replace("_", "-")
                    ).first()
                    if sub:
                        attrs["subcategory_obj"] = sub
        state = attrs.get("state")
        if state:
            st = State.objects.filter(slug=str(state).strip().lower()).first()
            if st:
                attrs["state_obj"] = st
                city = attrs.get("city")
                if city:
                    city_obj = City.objects.filter(
                        state=st, slug=_normalize(city).replace("_", "-")
                    ).first()
                    if city_obj:
                        attrs["city_obj"] = city_obj
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        output = []
        # Prefetch(to_attr) rows land on the instance (zero extra queries);
        # single/fresh objects fall back to one direct queryset.
        attribute_rows = getattr(instance, "prefetched_attribute_values", None)
        if attribute_rows is None:
            attribute_rows = getattr(instance, "_attribute_values_list", None)
        if attribute_rows is None:
            attribute_rows = list(instance.attribute_values.all())
        for row in attribute_rows:
            d = row.definition
            if d.data_type in ("number", "decimal"):
                value = float(row.value_number) if row.value_number is not None else None
            elif d.data_type == "boolean":
                value = row.value_bool
            elif d.data_type == "date":
                value = row.value_date.isoformat() if row.value_date else None
            elif d.data_type == "multiselect":
                value = row.value_list
            else:
                value = row.value_text
            output.append({
                "slug": d.slug,
                "label": d.label,
                "data_type": d.data_type,
                "unit": d.unit,
                "value": value,
            })
        data["attributes"] = output
        return data

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
        attrs = self._validate_attributes(attrs)
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

    @transaction.atomic
    def create(self, validated_data):
        attributes = validated_data.pop("attributes", None)
        validated_data = self._resolve_fk_fields(validated_data)
        product = Product.objects.create(**validated_data)
        self._save_attributes(product, attributes)
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        attributes = validated_data.pop("attributes", None)
        validated_data = self._resolve_fk_fields(validated_data)
        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()
        self._save_attributes(instance, attributes)
        return instance


# =============================================================================
# PRODUCT IMAGE SERIALIZER
# =============================================================================

class ProductImageSerializer(serializers.ModelSerializer):
    # Direct-to-storage uploads attach by object key instead of a file.
    image_key = serializers.CharField(write_only=True, required=False, max_length=512)

    class Meta:
        model = ProductImage
        fields = ["id", "product", "image", "image_key", "created_at"]
        read_only_fields = ("id", "created_at")
        extra_kwargs = {
            "image": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        from NaijaBay.media_uploads import is_own_direct_upload_key

        image = attrs.get("image")
        image_key = attrs.get("image_key")
        if not image and not image_key:
            raise serializers.ValidationError({"image": "Provide a file or an image_key."})
        if image_key is not None and not is_own_direct_upload_key(
            image_key.strip(), getattr(self.context.get("request"), "user", None).pk if self.context.get("request") else None
        ):
            raise serializers.ValidationError({"image_key": "This file was not uploaded by you."})
        return attrs

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
        image_key = validated_data.pop("image_key", None)
        if image_key:
            validated_data["image"] = image_key.strip()
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
