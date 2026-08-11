from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from accounts.models import User
from NaijaBay.utils import (
    CONDITION_CHOICES,
    CATEGORY_CHOICES,
    SUBCATEGORY_CHOICES,
    STATE_CHOICES,
    CITY_CHOICES,
    validate_contact_methods,
    product_images_upload_path,
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
    state = models.CharField(
        _("Product State"), max_length=25, choices=STATE_CHOICES, db_index=True
    )
    city = models.CharField(
        _("Product City"), max_length=20, choices=CITY_CHOICES, db_index=True
    )
    contact_methods = models.JSONField(
        _("Contact Methods"),
        default=list,
        validators=[validate_contact_methods],
    )
    contact_number = PhoneNumberField(_("Contact Number"))
    active = models.BooleanField(_("Active"), default=True, db_index=True)
    sold = models.BooleanField(_("Sold"), default=False, db_index=True)

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
