from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


# =============================================================================
# STATE
# =============================================================================

class State(models.Model):
    name = models.CharField(_("State Name"), max_length=30, unique=True)
    slug = models.SlugField(_("State Slug"), unique=True, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        verbose_name = _("State")
        verbose_name_plural = _("States")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["name", "slug"]),
        ]


# =============================================================================
# CITY
# =============================================================================

class City(models.Model):
    state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        related_name="cities",
        verbose_name=_("State"),
        db_index=True,
    )
    name = models.CharField(_("City Name"), max_length=20, db_index=True)
    slug = models.SlugField(_("City Slug"), max_length=50, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.name}, {self.state.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["state", "name"]
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        constraints = [
            models.UniqueConstraint(
                fields=["state", "name"], name="unique_city_per_state"
            ),
        ]
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=["state", "name"]),
            models.Index(fields=["state", "name", "slug"]),
        ]


# =============================================================================
# CATEGORY
# =============================================================================

class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=30, unique=True)
    slug = models.SlugField(_("Category Slug"), unique=True, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=["name", "slug"]),
        ]


# =============================================================================
# SUB CATEGORY
# =============================================================================

class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="sub_categories",
        verbose_name=_("Category"),
        db_index=True,
    )
    name = models.CharField(_("Sub Category Name"), max_length=20, db_index=True)
    slug = models.SlugField(_("Sub Category Slug"), max_length=50, db_index=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} — {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["category", "name"]
        verbose_name = _("Sub Category")
        verbose_name_plural = _("Sub Categories")
        constraints = [
            models.UniqueConstraint(
                fields=["category", "name"], name="unique_subcategory_per_category"
            ),
        ]
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=["category", "name"]),
            models.Index(fields=["category", "name", "slug"]),
        ]
