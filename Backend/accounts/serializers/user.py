from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from accounts.models import User
from products.serializers import ProductSerializer
from phonenumber_field.serializerfields import PhoneNumberField
from NaijaBay.utils import (
    FILE_UPLOAD_ALLOWED_EXTENSIONS,
    STATE_CHOICES,
    NOT_ALLOWED_USERNAMES,
    NOT_ALLOWED_EMAIL_DOMAINS,
)


# User Serailizer
class CustomUserSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    favorites = ProductSerializer(many=True, read_only=True, source='favorite_products')
    phone_number = PhoneNumberField()
    full_name = serializers.SerializerMethodField(read_only=True)
    unread_notifications = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "avatar",
            "full_name",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "state",
            "address",
            "date_joined",
            "last_login",
            "is_active",
            "unread_notifications",
            "products",
            "favorites",
        ]
        read_only_fields = (
            "id",
            "is_active",
            "date_joined",
            "last_login",
        )

    # Computed read-only fields

    @extend_schema_field(serializers.CharField())
    def get_full_name(self, obj):
        return obj.full_name

    @extend_schema_field(serializers.IntegerField(default=0))
    def get_unread_notifications(self, obj):
        return obj.unread_notifications

    # Field validators

    def validate_avatar(self, avatar):
        if avatar:
            avatar_name = avatar.name.lower()
            avatar_size = avatar.size

            if not avatar_name.endswith(tuple(FILE_UPLOAD_ALLOWED_EXTENSIONS)):
                raise serializers.ValidationError("This image format is not supported.")

            if avatar_size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    "This image size is too large. Max size is 2MB."
                )

        return avatar

    def validate_first_name(self, first_name):
        if first_name:
            first_name = first_name.strip().title()
        return first_name

    def validate_last_name(self, last_name):
        if last_name:
            last_name = last_name.strip().title()
        return last_name

    def validate_username(self, username):
        if username:
            username = username.strip().lower()

            if not username.isalpha():
                raise serializers.ValidationError(
                    "Username must be alphabet characters only."
                )

            if username in NOT_ALLOWED_USERNAMES:
                raise serializers.ValidationError("Username is not allowed, try again.")

            existing_user = User.objects.filter(username=username)

            if self.instance and self.instance.pk:
                existing_user = existing_user.exclude(pk=self.instance.pk)

            if existing_user.exists():
                raise serializers.ValidationError("Username already exists.")

        return username

    def validate_email(self, email):
        email = email.strip().lower()

        if email.endswith(tuple(NOT_ALLOWED_EMAIL_DOMAINS)):
            raise serializers.ValidationError("Email domain is not allowed.")

        existing_user = User.objects.filter(email=email)

        if self.instance and self.instance.pk:
            existing_user = existing_user.exclude(pk=self.instance.pk)

        if existing_user.exists():
            raise serializers.ValidationError("Email already exists.")

        return email

    def validate_state(self, state):
        if state:
            valid_states = [choice[0] for choice in STATE_CHOICES]
            if state not in valid_states:
                raise serializers.ValidationError("Invalid state.")

        return state

    def validate_address(self, address):
        if address:
            address = address.strip()
        return address

    # -------------------------------------------------------------------------
    # Update
    # -------------------------------------------------------------------------

    def update(self, instance, validated_data):

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance