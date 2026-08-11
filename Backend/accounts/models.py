import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import validate_email
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
from NaijaBay.utils import (
    NOTIFICATION_TYPES,
    STATE_CHOICES,
    CITY_CHOICES,
    STORE_TYPE_CHOICES,
    user_avatar_upload_path,
    store_banner_upload_path,
    store_logo_upload_path,
)


# =============================================================================
# USER MANAGER
# =============================================================================

class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address.'))
        if not username:
            raise ValueError(_('Users must have a username.'))

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('verified', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)


# =============================================================================
# USER MODEL
# =============================================================================

class User(AbstractBaseUser, PermissionsMixin):
    avatar = models.ImageField(_("Avatar"), upload_to=user_avatar_upload_path, blank=True)
    first_name = models.CharField(_("First Name"), blank=True, max_length=20)
    last_name = models.CharField(_("Last Name"), blank=True, max_length=20)
    username = models.CharField(
        _("Username"), unique=True, db_index=True, max_length=15
    )
    email = models.EmailField(
        _("Email Address"), unique=True, db_index=True, max_length=254,
        validators=[validate_email]
    )
    phone_number = PhoneNumberField(_("Phone Number"), blank=True)
    address = models.TextField(_("Address"), blank=True)
    state = models.CharField(_("State"), max_length=20, choices=STATE_CHOICES, blank=True)
    date_joined = models.DateTimeField(_("Date Joined"), auto_now_add=True)

    # Status flags
    is_active = models.BooleanField(_("Active"), default=True, db_index=True)
    verified = models.BooleanField(_("Verified"), default=False, db_index=True)
    is_staff = models.BooleanField(_("Staff"), default=False, db_index=True)

    # Social
    followers = models.ManyToManyField(
        'self', symmetrical=False, blank=True, related_name='following'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Object Manager
    objects = UserManager()

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.username

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def unread_notifications(self):
        return self.notifications.filter(read=False).count() if hasattr(self, 'notifications') else 0

    def __str__(self):
        return f"User: {self.username} <-> Status: {'✅' if self.is_active else '❌'}"

    class Meta:
        ordering = ['username', 'email', '-date_joined']
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['date_joined']),
            models.Index(fields=['username', 'email', 'state']),
            models.Index(fields=['username', 'email', 'verified', 'state']),
            models.Index(fields=['username', 'email', 'is_active', 'date_joined']),
        ]


# =============================================================================
# USER VERIFICATION (Auto-verify on payment)
# =============================================================================

class UserVerification(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification',
        verbose_name=_("User"),
    )
    is_verified = models.BooleanField(_("Is Verified"), default=False, db_index=True)
    verified_at = models.DateTimeField(_("Verified At"), blank=True, null=True)

    # Payment tracking
    amount_paid = models.DecimalField(
        _("Amount Paid"), max_digits=10, decimal_places=2, default=Decimal('5000.00')
    )
    transaction_reference = models.CharField(
        _("Transaction Reference"), max_length=100, blank=True, db_index=True
    )
    payment_gateway = models.CharField(
        _("Payment Gateway"), max_length=50, blank=True
    )
    paid_at = models.DateTimeField(_("Paid At"), blank=True, null=True)

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("User Verification")
        verbose_name_plural = _("User Verifications")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} — {'✅ Verified' if self.is_verified else '⏳ Not Verified'}"

    def confirm_payment(self, reference, gateway, amount):
        """
        Call this from your payment webhook or callback view.
        Once payment is confirmed, the user is instantly verified.
        """
        self.transaction_reference = reference
        self.payment_gateway = gateway
        self.amount_paid = amount
        self.paid_at = timezone.now()
        self.is_verified = True
        self.verified_at = timezone.now()
        self.save()

    def revoke_verification(self):
        """Admin helper to remove verification if needed."""
        self.is_verified = False
        self.verified_at = None
        self.save()

    def save(self, *args, **kwargs):
        # Auto-sync the User.verified flag whenever this record changes
        creating = self._state.adding
        super().save(*args, **kwargs)

        if self.user.verified != self.is_verified:
            self.user.verified = self.is_verified
            self.user.save(update_fields=['verified'])


# =============================================================================
# STORE MODEL
# =============================================================================

class Store(models.Model):
    store_user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name=_("Store User"), db_index=True, related_name='store_user'
    )
    store_name = models.CharField(
        _("Store Name"), max_length=100, db_index=True
    )
    store_slug = models.SlugField(
        _("Store Slug"), max_length=120, unique=True, db_index=True
    )
    store_description = models.TextField(
        _("Store Description"), max_length=1500
    )
    store_type = models.CharField(
        _("Store Type"), max_length=20, choices=STORE_TYPE_CHOICES, db_index=True
    )
    store_email = models.EmailField(
        _("Store Email Address"), validators=[validate_email], max_length=254
    )
    store_phone_number = PhoneNumberField(_("Store Phone Number"))
    store_whatsapp_number = PhoneNumberField(_("Store WhatsApp Number"))
    state = models.CharField(
        _("Store State"), max_length=25, choices=STATE_CHOICES, db_index=True
    )
    city = models.CharField(
        _("Store City"), max_length=100, choices=CITY_CHOICES, db_index=True
    )
    address = models.TextField(_("Store Address"))
    logo = models.ImageField(
        _("Store Logo"), upload_to=store_logo_upload_path, blank=True, null=True
    )
    banner = models.ImageField(
        _("Store Banner"), upload_to=store_banner_upload_path, blank=True, null=True
    )
    is_active = models.BooleanField(
        _("Store Active"), default=True, db_index=True
    )
    members = models.ManyToManyField(
        User, blank=True, related_name='store_members'
    )
    created_at = models.DateTimeField(
        _("Store Created At"), auto_now_add=True, db_index=True
    )
    updated_at = models.DateTimeField(
        _("Store Updated At"), auto_now=True, db_index=True
    )

    @property
    def total_members(self):
        return self.members.count()

    def __str__(self):
        return (
            f"Store Owner: {self.store_user.username} <-> "
            f"Store Name: {self.store_name} <-> "
            f"Status: {'✅' if self.is_active else '❌'}"
        )

    def save(self, *args, **kwargs):
        if not self.store_slug:
            base_slug = slugify(self.store_name)
            slug = base_slug
            counter = 1
            while Store.objects.filter(store_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.store_slug = slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        ordering = ["is_active", '-created_at']
        indexes = [
            models.Index(fields=['store_name', 'store_type', '-created_at']),
            models.Index(fields=['store_user', 'store_name', 'store_type', 'state', 'city']),
        ]


# =============================================================================
# NOTIFICATIONS MODEL
# =============================================================================

class Notifications(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='notifications',
        verbose_name=_("User"), db_index=True
    )
    notification_type = models.CharField(
        _("Notification Type"), max_length=30, choices=NOTIFICATION_TYPES,
        default='system_notification'
    )
    message = models.TextField(_("Message"))
    read = models.BooleanField(_("Read"), default=False, db_index=True)
    timestamp = models.DateTimeField(_("Time Stamp"), auto_now_add=True, db_index=True)

    def __str__(self):
        return (
            f"User: {self.user.username} <-> "
            f"Type: {self.get_notification_type_display()} <-> "
            f"Read: {'✅' if self.read else '❌'}"
        )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['user', 'read', '-timestamp']),
        ]