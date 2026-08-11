from django.contrib import admin
from django.utils.html import format_html
from .models import User, Notifications, Store, UserVerification
from django.utils.translation import gettext_lazy as _
# =============================================================================
# USER ADMIN
# =============================================================================


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "full_name",
        "verified",
        "is_staff",
        "is_active",
        "date_joined",
        "last_login",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "verified",
        "state",
        "date_joined",
    )
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    readonly_fields = (
        "date_joined",
        "last_login",
        "followers_count",
        "following_count",
    )
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        (
            "Profile",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                    "phone_number",
                    "address",
                    "state",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                    "verified",
                    "is_staff",
                    "is_superuser",
                    "date_joined",
                    "last_login",
                )
            },
        ),
        (
            "Social",
            {
                "fields": ("followers", "followers_count", "following_count"),
                "classes": ("collapse",),
            },
        ),
        (
            "Permissions",
            {
                "fields": ("groups", "user_permissions"),
                "classes": ("collapse",),
            },
        ),
    )
    filter_horizontal = ("followers", "groups", "user_permissions")

    @admin.display(description=_("Full Name"))
    def full_name(self, obj):
        return obj.full_name


# =============================================================================
# USER VERIFICATION ADMIN
# =============================================================================


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "is_verified",
        "status_badge",
        "amount_paid",
        "payment_gateway",
        "verified_at",
        "paid_at",
        "created_at",
    )
    list_filter = ("is_verified", "payment_gateway", "created_at", "verified_at")
    search_fields = ("user__username", "user__email", "transaction_reference")
    readonly_fields = ("verified_at", "paid_at", "created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = ["revoke_verification"]

    fieldsets = (
        (None, {"fields": ("user", "is_verified")}),
        (
            "Payment Info",
            {
                "fields": (
                    "amount_paid",
                    "transaction_reference",
                    "payment_gateway",
                    "paid_at",
                )
            },
        ),
        (
            "Verification Timeline",
            {"fields": ("verified_at", "created_at", "updated_at")},
        ),
    )

    @admin.display(description=_("Status"))
    def status_badge(self, obj):
        if obj.is_verified:
            return format_html(
                '<span style="color: green; font-weight: bold;">✅ VERIFIED</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">⏳ PENDING</span>'
        )

    @admin.action(description=_("Revoke selected verifications"))
    def revoke_verification(self, request, queryset):
        for verification in queryset:
            verification.revoke_verification()
        self.message_user(
            request, f"{queryset.count()} verification(s) revoked successfully."
        )


# =============================================================================
# NOTIFICATIONS ADMIN
# =============================================================================


@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "read", "timestamp")
    list_filter = ("notification_type", "read", "timestamp")
    search_fields = ("user__username", "user__email", "message")
    readonly_fields = ("timestamp",)
    date_hierarchy = "timestamp"
    actions = ["mark_as_read", "mark_as_unread"]

    @admin.action(description=_("Mark selected notifications as read"))
    def mark_as_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, f"{updated} notification(s) marked as read.")

    @admin.action(description=_("Mark selected notifications as unread"))
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, f"{updated} notification(s) marked as unread.")


# =============================================================================
# STORE ADMIN
# =============================================================================
@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = (
        "owner_username",
        "store_name",
        "store_type",
        "store_email",
        "state",
        "city",
        "is_active",
        "total_members",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "store_type",
        "state",
        "city",
        "is_active",
        "created_at",
    )
    search_fields = (
        "store_name",
        "store_email",
        "store_slug",
        "store_user__username",
        "store_user__email",
    )
    readonly_fields = ("store_slug", "created_at", "updated_at", "total_members")
    autocomplete_fields = ("store_user", "members")
    date_hierarchy = "created_at"

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "store_user",
                    "store_name",
                    "store_slug",
                    "store_description",
                    "store_type",
                )
            },
        ),
        (
            "Contact",
            {
                "fields": (
                    "store_email",
                    "store_phone_number",
                    "store_whatsapp_number",
                    "address",
                    "state",
                    "city",
                )
            },
        ),
        ("Media", {"fields": ("logo", "banner")}),
        (
            "Status",
            {
                "fields": (
                    "is_active",
                    "members",
                    "total_members",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(description=_("Owner"))
    def owner_username(self, obj):
        return obj.store_user.username
