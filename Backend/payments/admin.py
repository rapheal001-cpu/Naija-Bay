from django.contrib import admin
from .models import BoostPlan, ListingBoost, Payment, WebhookEvent


@admin.register(BoostPlan)
class BoostPlanAdmin(admin.ModelAdmin):
    """Edit names, prices, durations and benefits here - nothing is hardcoded."""

    list_display = ("name", "price", "duration_days", "boost_level", "is_active", "sort_order")
    list_editable = ("price", "duration_days", "boost_level", "is_active", "sort_order")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "purpose", "amount", "status", "created_at")
    list_filter = ("purpose", "status")
    search_fields = ("reference", "user__email", "user__username")
    readonly_fields = [f.name for f in Payment._meta.fields]

    def has_add_permission(self, request):
        return False


@admin.register(ListingBoost)
class ListingBoostAdmin(admin.ModelAdmin):
    list_display = ("product", "plan", "user", "status", "started_at", "expires_at")
    list_filter = ("status", "plan")
    readonly_fields = ("payment",)


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_key", "event_type", "reference", "received_at")
    search_fields = ("event_key", "reference")
