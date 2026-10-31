from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Product, ProductImage, ProductReport, ProductRating

# =============================================================================
# PRODUCT ADMIN
# =============================================================================


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "product_name",
        "owner",
        "price",
        "category",
        "sub_category",
        "product_slug",
        "quantity",
        "favorites_count_display",
        "views_count_display",
        "promoted",
        "delivery_available",
        "active",
        "sold",
        "expires_at",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "active",
        "sold",
        "promoted",
        "delivery_available",
        "category",
        "sub_category",
        "condition",
        "state",
        "created_at",
    )
    search_fields = (
        "product_name",
        "description",
        "product_slug",
        "product_user__username",
        "product_user__email",
    )
    readonly_fields = (
        "product_slug",
        "favorites_count",
        "views_count",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"
    autocomplete_fields = ("product_user",)
    list_select_related = ("product_user",)

    # Removed prepopulated_fields because your model's save() already handles
    # slug generation with collision detection. The admin prepopulate would
    # bypass that logic and risk duplicate slugs.

    @admin.display(description=_("Owner"))
    def owner(self, obj):
        return obj.product_user.username

    @admin.display(description=_("Favorites"))
    def favorites_count_display(self, obj):
        return obj.favorites_count

    @admin.display(description=_("Views"))
    def views_count_display(self, obj):
        return obj.views_count


# =============================================================================
# PRODUCT IMAGE ADMIN
# =============================================================================


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("product__product_name", "product__product_slug")
    readonly_fields = ("created_at", "image_preview")
    autocomplete_fields = ("product",)
    list_select_related = ("product",)

    @admin.display(description=_("Preview"))
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 120px; border-radius: 4px;" />',
                obj.image.url,
            )


# =============================================================================
# PRODUCT REPORT ADMIN
# =============================================================================


@admin.register(ProductReport)
class ProductReportAdmin(admin.ModelAdmin):
    list_display = ("product", "reporter", "reason", "status", "created_at")
    list_filter = ("reason", "status", "created_at")
    search_fields = (
        "product__product_name",
        "reporter__username",
        "details",
    )
    readonly_fields = ("created_at",)
    autocomplete_fields = ("product", "reporter")
    list_select_related = ("product", "reporter")
    date_hierarchy = "created_at"
    actions = ["mark_resolved", "mark_dismissed"]

    @admin.action(description=_("Mark selected reports as resolved"))
    def mark_resolved(self, request, queryset):
        updated = queryset.update(status="resolved")
        self.message_user(request, f"{updated} report(s) resolved.")

    @admin.action(description=_("Dismiss selected reports"))
    def mark_dismissed(self, request, queryset):
        updated = queryset.update(status="dismissed")
        self.message_user(request, f"{updated} report(s) dismissed.")


@admin.register(ProductRating)
class ProductRatingAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "value", "updated_at")
    list_filter = ("value",)
    search_fields = ("product__product_name", "user__username")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("product", "user")
    list_select_related = ("product", "user")
