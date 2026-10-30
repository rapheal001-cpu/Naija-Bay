from django.contrib import admin
from django.utils.html import format_html
from .models import User, Notifications, Store, Follow
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
        "is_staff",
        "is_active",
        "verified",
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
                    "is_staff",
                    "is_superuser",
                    "verified",
                    "date_joined",
                    "last_login",
                )
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
    filter_horizontal = ("groups", "user_permissions")

    @admin.display(description=_("Full Name"))
    def full_name(self, obj):
        return obj.full_name


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
    list_display = ("name", "owner", "verified", "state", "products_count", "created_at")
    list_filter = ("verified", "state", "created_at")
    search_fields = ("name", "slug", "user__username", "user__email")
    readonly_fields = ("slug", "created_at", "updated_at")
    autocomplete_fields = ("user",)
    list_select_related = ("user",)
    date_hierarchy = "created_at"

    @admin.display(description=_("Owner"))
    def owner(self, obj):
        return obj.user.username

    @admin.display(description=_("Products"))
    def products_count(self, obj):
        return obj.products_count


# =============================================================================
# FOLLOW ADMIN
# =============================================================================


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")
    autocomplete_fields = ("follower", "following")
    list_select_related = ("follower", "following")
    date_hierarchy = "created_at"
