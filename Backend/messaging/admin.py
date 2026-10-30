from django.contrib import admin

from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("sender", "body", "read", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "seller", "product", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("buyer__username", "seller__username", "product__product_name")
    inlines = [MessageInline]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "read", "created_at")
    list_filter = ("read", "created_at")
    search_fields = ("sender__username", "body")
