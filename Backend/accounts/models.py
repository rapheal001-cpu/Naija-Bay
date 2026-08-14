from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
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