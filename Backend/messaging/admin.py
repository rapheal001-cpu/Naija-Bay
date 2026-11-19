from django.contrib import admin

from .models import Conversation, ConversationUserState, Message, UserBlock


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


@admin.register(UserBlock)
class UserBlockAdmin(admin.ModelAdmin):
    list_display = ("blocker", "blocked_user", "created_at")
    search_fields = ("blocker__username", "blocked_user__username")


@admin.register(ConversationUserState)
class ConversationUserStateAdmin(admin.ModelAdmin):
    list_display = ("conversation", "user", "deleted_at")
    search_fields = ("user__username",)
