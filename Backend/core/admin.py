from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import State, City, Category, SubCategory

# =============================================================================
# STATE ADMIN
# =============================================================================


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("slug", "created_at")
    date_hierarchy = "created_at"


# =============================================================================
# CITY ADMIN
# =============================================================================


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "state", "slug", "created_at")
    list_filter = ("state", "created_at")
    search_fields = ("name", "slug", "state__name")
    readonly_fields = ("slug", "created_at")
    autocomplete_fields = ("state",)
    date_hierarchy = "created_at"


# =============================================================================
# CATEGORY ADMIN
# =============================================================================


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("slug", "created_at")
    date_hierarchy = "created_at"


# =============================================================================
# SUB CATEGORY ADMIN
# =============================================================================


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name", "slug", "category__name")
    readonly_fields = ("slug", "created_at")
    autocomplete_fields = ("category",)
    date_hierarchy = "created_at"
