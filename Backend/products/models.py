from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import User
from core.models import AttributeDefinition, Category, City, State, SubCategory
from NaijaBay.utils import (
    CONDITION_CHOICES,
    CATEGORY_CHOICES,
    SUBCATEGORY_CHOICES,
    STATE_CHOICES,
    CITY_CHOICES,
    validate_contact_methods,
    product_images_upload_path,
    NON_PURCHASABLE_CATEGORIES,
)


# =============================================================================
# PRODUCT
# =============================================================================

class Product(models.Model):
    product_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Product User"),
        related_name="products",
        db_index=True,
    )
    product_name = models.CharField(_("Product Name"), max_length=200, db_index=True)
    product_slug = models.SlugField(
        _("Product Slug"), max_length=200, unique=True, db_index=True
    )
    description = models.TextField(_("Product Description"))
    price = models.DecimalField(
        _("Product Price"),
        max_digits=15,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("1000.00")),
            MaxValueValidator(Decimal("999999999")),
        ],
    )
    category = models.CharField(
        _("Category"), max_length=30, choices=CATEGORY_CHOICES, db_index=True
    )
    sub_category = models.CharField(
        _("Sub Category"), max_length=20, choices=SUBCATEGORY_CHOICES, db_index=True
    )
    # Relational references to the seeded taxonomy (nullable during migration).
    category_obj = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Category (Relational)"),
        db_index=True,
    )
    subcategory_obj = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("Sub Category (Relational)"),
        db_index=True,
    )
    condition = models.CharField(
        _("Product Condition"), max_length=20, choices=CONDITION_CHOICES, db_index=True
    )
    color = models.CharField(_("Product Color"), max_length=20)
    quantity = models.PositiveIntegerField(
        _("Product Quantity"),
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10000)],
    )
    negotiable = models.BooleanField(_("Price Negotiable"), default=False)
    original_price = models.DecimalField(
        _("Original Price"),
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal("1000.00")),
            MaxValueValidator(Decimal("999999999")),
        ],
        help_text=_("Optional higher 'was' price. When set above the sale price the listing shows a discount."),
    )
    sold_count = models.PositiveIntegerField(_("Sold Count"), default=0)
    state = models.CharField(
        _("Product State"), max_length=25, choices=STATE_CHOICES, db_index=True
    )
    city = models.CharField(
        _("Product City"), max_length=20, choices=CITY_CHOICES, db_index=True
    )
    # Relational references to the seeded location taxonomy (nullable during migration).
    state_obj = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("State (Relational)"),
        db_index=True,
    )
    city_obj = models.ForeignKey(
        City,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name=_("City (Relational)"),
        db_index=True,
    )
    contact_methods = models.JSONField(
        _("Contact Methods"),
        default=list,
        validators=[validate_contact_methods],
    )
    contact_number = PhoneNumberField(_("Contact Number"))
    active = models.BooleanField(_("Active"), default=True, db_index=True)
    sold = models.BooleanField(_("Sold"), default=False, db_index=True)
    promoted = models.BooleanField(_("Promoted"), default=False, db_index=True)
    promoted_until = models.DateTimeField(
        _("Promoted Until"),
        null=True,
        blank=True,
        help_text=_("When a paid ad boost ends. Empty means promoted without an end date."),
    )
    boost_level = models.PositiveSmallIntegerField(
        _("Boost Level"),
        default=0,
        db_index=True,
        help_text=_("Higher levels appear first among promoted listings."),
    )
    delivery_available = models.BooleanField(_("Delivery Available"), default=False)
    expires_at = models.DateTimeField(_("Expires At"), null=True, blank=True)

    # Social
    favorites = models.ManyToManyField(
        User,
        related_name="favorite_products",
        verbose_name=_("Product Favorites"),
        blank=True,
    )
    views = models.ManyToManyField(
        User,
        related_name="viewed_products",
        verbose_name=_("Product Views"),
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return round(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    @property
    def is_discounted(self):
        return self.discount_percent > 0

    @property
    def favorites_count(self):
        return self.favorites.count()

    @property
    def views_count(self):
        return self.views.count()

    @property
    def images_count(self):
        return self.images.count() if hasattr(self, 'images') else 0

    @property
    def has_contact_number(self):
        return any(
            method in self.contact_methods for method in ("phone_call", "whatsapp")
        )

    @property
    def listing_status(self):
        """Marketplace-facing status: active, sold, expired or inactive."""
        from django.utils import timezone

        if self.sold:
            return "sold"
        if not self.active:
            return "inactive"
        if self.expires_at and self.expires_at <= timezone.now():
            return "expired"
        return "active"

    @property
    def is_expired(self):
        return self.listing_status == "expired"

    @property
    def is_boosted(self):
        from django.utils import timezone

        return bool(
            self.promoted
            and (self.promoted_until is None or self.promoted_until > timezone.now())
        )

    @property
    def is_purchasable(self):
        """True when the item can be bought through the cart and checkout."""
        return (
            self.listing_status == "active"
            and self.quantity >= 1
            and self.category not in NON_PURCHASABLE_CATEGORIES
        )

    # -------------------------------------------------------------------------
    # Methods
    # -------------------------------------------------------------------------

    def __str__(self):
        return (
            f"Name: {self.product_name} <-> "
            f"Active: {'✅' if self.active else '❌'} <-> "
            f"Sold: {'✅' if self.sold else '❌'}"
        )

    def save(self, *args, **kwargs):
        if not self.product_slug:
            base_slug = slugify(self.product_name)
            slug = base_slug
            counter = 1

            while (
                Product.objects.filter(product_slug=slug).exclude(pk=self.pk).exists()
            ):
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.product_slug = slug

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        indexes = [
            models.Index(fields=["product_name"]),
            models.Index(fields=["product_user"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["active"]),
            models.Index(fields=["product_user", "product_name"]),
            models.Index(fields=["category", "sub_category"]),
            models.Index(fields=["product_user", "category", "sub_category", "active"]),
            models.Index(fields=["state", "city"]),
            models.Index(fields=["category", "state", "city"]),
            models.Index(fields=["category_obj", "subcategory_obj"]),
            models.Index(fields=["state_obj", "city_obj"]),
        ]


# =============================================================================
# PRODUCT IMAGE
# =============================================================================

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Product"),
        db_index=True,
    )
    image = models.ImageField(_("Product Image"), upload_to=product_images_upload_path)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.product.product_name} - Image #{self.id}"

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["product"]),
            models.Index(fields=["product", "created_at"]),
        ]


# =============================================================================
# PRODUCT REPORT (ABUSE)
# =============================================================================

class ProductReport(models.Model):
    REASON_CHOICES = [
        ("scam", "Scam or fraud"),
        ("prohibited", "Prohibited item"),
        ("wrong_category", "Wrong category"),
        ("counterfeit", "Counterfeit product"),
        ("offensive", "Offensive content"),
        ("duplicate", "Duplicate listing"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewing", "Reviewing"),
        ("resolved", "Resolved"),
        ("dismissed", "Dismissed"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("Product"),
        db_index=True,
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="product_reports",
        verbose_name=_("Reporter"),
        db_index=True,
    )
    reason = models.CharField(_("Reason"), max_length=20, choices=REASON_CHOICES)
    details = models.TextField(_("Details"), blank=True)
    status = models.CharField(
        _("Status"), max_length=12, choices=STATUS_CHOICES, default="pending", db_index=True
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.product.product_name} reported by {self.reporter.username}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Product Report")
        verbose_name_plural = _("Product Reports")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "reporter"], name="unique_report_per_user"
            ),
        ]
        indexes = [
            models.Index(fields=["product", "reporter"]),
            models.Index(fields=["status", "-created_at"]),
        ]


# =============================================================================
# PRODUCT RATING
# =============================================================================

class ProductRating(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=_("Product"),
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="product_ratings",
        verbose_name=_("User"),
        db_index=True,
    )
    value = models.PositiveSmallIntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} rated {self.value}/5 by {self.user.username}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Product Rating")
        verbose_name_plural = _("Product Ratings")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"], name="unique_rating_per_user"
            ),
        ]
        indexes = [
            models.Index(fields=["product", "user"]),
        ]


# =============================================================================
# PRODUCT ATTRIBUTE VALUE
# =============================================================================

class ProductAttribute(models.Model):
    """One typed specification value for a product (e.g. Cars → year=2019).

    Values are stored in typed columns so category-specific filters
    (``attr_year_gte``, ``attr_transmission``) are indexed range/equality
    lookups instead of JSON or string scans.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="attribute_values",
        verbose_name=_("Product"),
        db_index=True,
    )
    definition = models.ForeignKey(
        AttributeDefinition,
        on_delete=models.CASCADE,
        related_name="product_values",
        verbose_name=_("Attribute Definition"),
        db_index=True,
    )
    value_text = models.TextField(_("Text Value"), null=True, blank=True)
    value_number = models.DecimalField(
        _("Number Value"), max_digits=15, decimal_places=2, null=True, blank=True
    )
    value_bool = models.BooleanField(_("Boolean Value"), null=True, blank=True)
    value_date = models.DateField(_("Date Value"), null=True, blank=True)
    value_list = models.JSONField(_("List Value"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def __str__(self):
        return f"{self.product.product_name} — {self.definition.label}"

    class Meta:
        ordering = ["definition__sort_order", "definition__name"]
        verbose_name = _("Product Attribute")
        verbose_name_plural = _("Product Attributes")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "definition"],
                name="unique_product_attribute",
            ),
        ]
        indexes = [
            models.Index(fields=["definition", "value_number"]),
            models.Index(fields=["definition", "value_text"]),
            models.Index(fields=["product"]),
            models.Index(fields=["definition"]),
        ]
