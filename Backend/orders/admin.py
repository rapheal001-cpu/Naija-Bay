from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ("product", "seller", "product_name", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("reference", "buyer", "status", "payment_status", "total", "created_at")
    list_filter = ("status", "payment_status")
    search_fields = ("reference", "buyer__email", "buyer__username", "recipient_name")
    readonly_fields = ("reference", "subtotal", "delivery_fee", "total", "currency", "paid_at", "created_at")
    inlines = [OrderItemInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
    search_fields = ("user__email", "user__username")
    inlines = [CartItemInline]
