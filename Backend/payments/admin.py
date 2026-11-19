from django.contrib import admin
from .models import (
    BoostPlan, ListingBoost, Payment, WebhookEvent,
    CreditAccount, CreditTransaction, ReferralBonus,
    BoostAutoRenewal, ProSalesCampaign,
)


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


@admin.register(CreditAccount)
class CreditAccountAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "updated_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("updated_at",)


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ("account", "transaction_type", "amount", "reference", "created_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("account__user__username", "reference")


@admin.register(ReferralBonus)
class ReferralBonusAdmin(admin.ModelAdmin):
    list_display = ("referrer", "referred", "amount", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("referrer__username", "referred__username")


@admin.register(BoostAutoRenewal)
class BoostAutoRenewalAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "product", "status", "next_charge_at", "created_at")
    list_filter = ("status", "plan", "created_at")
    search_fields = ("user__username", "product__product_name")


@admin.register(ProSalesCampaign)
class ProSalesCampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "product", "status", "daily_budget", "bid_amount", "clicks", "spend", "ends_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "user__username", "product__product_name")
