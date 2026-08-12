from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .user import CustomUserSerializer
from products.serializers import ProductSerializer
from accounts.models import User
from accounts.models import Notifications, Store
from core.models import State, City
from phonenumber_field.serializerfields import PhoneNumberField
from NaijaBay.utils import (
    STATE_CHOICES,
    CITY_CHOICES,
    STORE_TYPE_CHOICES,
    FILE_UPLOAD_ALLOWED_EXTENSIONS,
    _normalize,
)


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


# Store Members Serailizer
class StoreMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'avatar', 'full_name', 'username', 'is_active', 'verified', 'date_joined']


# Store Serializer
class StoreSerializer(serializers.ModelSerializer):
    store_user = CustomUserSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True, source="store_user.products")
    members = StoreMembersSerializer(many=True, read_only=True, source="store_members")
    store_phone_number = PhoneNumberField()
    state = serializers.ChoiceField(choices=STATE_CHOICES)
    city = serializers.ChoiceField(choices=CITY_CHOICES)
    store_type = serializers.ChoiceField(choices=STORE_TYPE_CHOICES)
    store_email = serializers.EmailField(write_only=True, style={"input_type": "email"}, max_length=254)
    store_whatsapp_number = PhoneNumberField(required=False)
    total_members = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "store_user",
            'products',
            "store_name",
            "store_slug",
            "store_description",
            "store_type",
            "store_email",
            "store_phone_number",
            "store_whatsapp_number",
            "members",
            "total_members",
            "state",
            "city",
            "address",
            "logo",
            "banner",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "store_user",
            "store_slug",
            "members",
            "is_active",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_total_members(self, obj):
        return obj.total_members

    # Field validators

    def validate_store_name(self, store_name):
        store_name = store_name.strip().title()
        if not store_name:
            raise serializers.ValidationError("Store name is required.")
        return store_name

    def validate_store_description(self, store_description):
        store_description = store_description.strip()
        if store_description and len(store_description) < 10:
            raise serializers.ValidationError(
                "Store description must be at least 10 characters."
            )
        return store_description

    def validate_store_type(self, store_type):
        store_types = [choice[0] for choice in STORE_TYPE_CHOICES if choice[0]]
        if store_type not in store_types:
            raise serializers.ValidationError("Invalid store type.")
        return store_type

    def validate_store_email(self, store_email):
        store_email = store_email.strip().lower()
        if "@" not in store_email:
            raise serializers.ValidationError("Enter a valid email address.")
        return store_email

    def validate_state(self, state):
        if not state:
            raise serializers.ValidationError(
                "Please select the state your store is located."
            )

        slugify_state = _normalize(state)

        if not State.objects.filter(slug=slugify_state).exists():
            raise serializers.ValidationError(f"'{state}' is not a valid state.")
        return state

    def validate_city(self, city):
        if not city:
            raise serializers.ValidationError(
                "Please select the city your store is located."
            )

        slugify_city = _normalize(city)

        if not City.objects.filter(slug=slugify_city).exists():
            raise serializers.ValidationError(f"'{city}' is not a valid city.")
        return city

    def validate_logo(self, logo):
        if not logo:
            raise serializers.ValidationError('Please add your store logo.')

        logo_name = logo.name.lower()
        logo_size = logo.size

        if not logo_name.endswith(tuple(FILE_UPLOAD_ALLOWED_EXTENSIONS)):
            allowed = ", ".join(FILE_UPLOAD_ALLOWED_EXTENSIONS)
            raise serializers.ValidationError(
                f"This {logo_name} format is not accepted. Choose image format like: {allowed}"
            )

        if logo_size > 2 * 1024 * 1024:
            raise serializers.ValidationError(f"Image size too large. Max is 2MB.")

        return logo

    def validate_banner(self, banner):
        if not banner:
            raise serializers.ValidationError('Please add your store banner.')

        banner_name = banner.name.lower()
        banner_size = banner.size

        if not banner_name.endswith(tuple(FILE_UPLOAD_ALLOWED_EXTENSIONS)):
            allowed = ", ".join(FILE_UPLOAD_ALLOWED_EXTENSIONS)
            raise serializers.ValidationError(
                f"This {banner_name} format is not accepted. Choose image format like: {allowed}"
            )

        if banner_size > 2 * 1024 * 1024:
            raise serializers.ValidationError(f"Banner size too large. Max is 2MB.")

        return banner

    # Object-level validation

    def validate(self, attrs):
        state = attrs.get("state", getattr(self.instance, 'state', ''))
        city = attrs.get("city", getattr(self.instance, 'city', ''))

        if state and city:

            slugify_state = _normalize(state)
            slugify_city = _normalize(city)

            try:
                state_instance = State.objects.get(slug=slugify_state)
            except State.DoesNotExist:
                raise serializers.ValidationError(
                    {"state": f"'{state}' does not exist."}
                )

            if not City.objects.filter(
                state=state_instance, slug=slugify_city
            ).exists():
                raise serializers.ValidationError(
                    {
                        "city": f"'{city}' does not belong to state '{state_instance.name}'."
                    }
                )

        return attrs

    def create(self, validated_data):
        return Store.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance
