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


# =============================================================================
# ATTRIBUTE DEFINITION
# =============================================================================

class AttributeDefinition(models.Model):
    """One category-specific specification field (e.g. Vehicles → Fuel Type).

    A definition is scoped to a Category, and optionally narrowed to a single
    SubCategory. Products store their values in ProductAttribute rows.
    """

    DATA_TYPE_CHOICES = [
        ("text", "Text"),
        ("number", "Number"),
        ("decimal", "Decimal"),
        ("boolean", "Boolean"),
        ("date", "Date"),
        ("select", "Select"),
        ("multiselect", "Multiselect"),
    ]

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="attribute_definitions",
        verbose_name=_("Category"),
        null=True,
        blank=True,
        db_index=True,
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.CASCADE,
        related_name="attribute_definitions",
        verbose_name=_("Sub Category"),
        null=True,
        blank=True,
        db_index=True,
    )
    name = models.CharField(_("Attribute Name"), max_length=60)
    slug = models.SlugField(_("Attribute Slug"), max_length=60, db_index=True)
    label = models.CharField(_("Display Label"), max_length=80)
    data_type = models.CharField(
        _("Data Type"), max_length=15, choices=DATA_TYPE_CHOICES, default="text", db_index=True
    )
    required = models.BooleanField(_("Required"), default=False)
    filterable = models.BooleanField(_("Filterable"), default=True, db_index=True)
    sortable = models.BooleanField(_("Sortable"), default=False)
    unit = models.CharField(_("Unit"), max_length=20, blank=True)
    min_value = models.DecimalField(
        _("Min Value"), max_digits=15, decimal_places=2, null=True, blank=True
    )
    max_value = models.DecimalField(
        _("Max Value"), max_digits=15, decimal_places=2, null=True, blank=True
    )
    sort_order = models.PositiveSmallIntegerField(_("Sort Order"), default=0)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        scope = self.sub_category.name if self.sub_category else self.category.name
        return f"{scope} — {self.label}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["category", "sub_category", "sort_order", "name"]
        verbose_name = _("Attribute Definition")
        verbose_name_plural = _("Attribute Definitions")
        constraints = [
            models.UniqueConstraint(
                fields=["category", "sub_category", "slug"],
                name="unique_attribute_per_scope",
            ),
        ]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category", "sub_category"]),
            models.Index(fields=["data_type", "filterable"]),
        ]


# =============================================================================
# ATTRIBUTE OPTION
# =============================================================================

class AttributeOption(models.Model):
    """A selectable choice for select/multiselect attribute definitions."""

    definition = models.ForeignKey(
        AttributeDefinition,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("Attribute Definition"),
        db_index=True,
    )
    value = models.SlugField(_("Option Value"), max_length=60)
    label = models.CharField(_("Option Label"), max_length=80)
    sort_order = models.PositiveSmallIntegerField(_("Sort Order"), default=0)

    def __str__(self):
        return f"{self.definition.label}: {self.label}"

    class Meta:
        ordering = ["definition", "sort_order", "label"]
        verbose_name = _("Attribute Option")
        verbose_name_plural = _("Attribute Options")
        constraints = [
            models.UniqueConstraint(
                fields=["definition", "value"], name="unique_option_per_definition"
            ),
        ]
        indexes = [
            models.Index(fields=["definition", "value"]),
        ]
