from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import validate_email
from NaijaBay.utils import (
    NOTIFICATION_TYPES,
    STATE_CHOICES,
    user_avatar_upload_path,
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
    is_staff = models.BooleanField(_("Staff"), default=False, db_index=True)
    verified = models.BooleanField(_("Verified Seller"), default=False, db_index=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Object Manager
    objects = UserManager()

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.username

    @property
    def unread_notifications(self):
        return self.notifications.filter(read=False).count() if hasattr(self, 'notifications') else 0

    @property
    def followers_count(self):
        return self.followers.count()

    @property
    def following_count(self):
        return self.following.count()

    @property
    def has_store(self):
        return hasattr(self, 'store')

    def __str__(self):
        return f"User: {self.username} <-> Status: {'✅' if self.is_active else '❌'}"

    class Meta:
        ordering = ['username', 'email', '-date_joined']
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        indexes = [
            models.Index(fields=['date_joined']),
            models.Index(fields=['username', 'email', 'state']),
            models.Index(fields=['username', 'email', 'is_active', 'date_joined']),
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

# =============================================================================
# SELLER STORE
# =============================================================================

class Store(models.Model):
    """A public shop page that a seller can attach to their account."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="store",
        verbose_name=_("Store Owner"),
    )
    name = models.CharField(_("Store Name"), max_length=60, unique=True)
    slug = models.SlugField(_("Store Slug"), max_length=80, unique=True, db_index=True)
    description = models.TextField(_("Store Description"), blank=True)
    logo = models.ImageField(
        _("Store Logo"), upload_to="stores/logos/", blank=True, null=True
    )
    banner = models.ImageField(
        _("Store Banner"), upload_to="stores/banners/", blank=True, null=True
    )
    verified = models.BooleanField(_("Verified Store"), default=False, db_index=True)
    state = models.CharField(
        _("Store State"), max_length=20, choices=STATE_CHOICES, blank=True
    )
    address = models.TextField(_("Store Address"), blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Store.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def products_count(self):
        return self.user.products.filter(active=True, sold=False).count()

    class Meta:
        ordering = ["name"]
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["verified", "name"]),
        ]


# =============================================================================
# FOLLOW (SELLER SUBSCRIPTIONS)
# =============================================================================

class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name=_("Follower"),
        db_index=True,
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name=_("Following"),
        db_index=True,
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Follow")
        verbose_name_plural = _("Follows")
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_follow"
            ),
            models.CheckConstraint(
                condition=~models.Q(follower=models.F("following")),
                name="prevent_self_follow",
            ),
        ]
        indexes = [
            models.Index(fields=["follower", "following"]),
            models.Index(fields=["following", "follower"]),
        ]
