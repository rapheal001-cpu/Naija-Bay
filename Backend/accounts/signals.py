from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from NaijaBay.utils import NOTIFICATION_TEMPLATES
from .models import User, Notifications


# =============================================================================
# USER WELCOME NOTIFICATION
# =============================================================================

@receiver(post_save, sender=User)
def send_new_user_notification(sender, instance, created, **kwargs):
    """Send a welcome notification to every newly created user."""

    if created:
        message = NOTIFICATION_TEMPLATES["system_notification"][0].format(username=instance.username)
        Notifications.objects.create(user=instance, message=message)