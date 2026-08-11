from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from NaijaBay.utils import NOTIFICATION_TEMPLATES
from .models import User, Notifications, Store


# =============================================================================
# USER WELCOME NOTIFICATION
# =============================================================================

@receiver(post_save, sender=User)
def send_new_user_notification(sender, instance, created, **kwargs):
    """Send a welcome notification to every newly created user."""

    if created:
        message = NOTIFICATION_TEMPLATES["system_notification"][0].format(username=instance.username)
        Notifications.objects.create(user=instance, message=message)


# =============================================================================
# STORE CREATION NOTIFICATION
# =============================================================================

@receiver(post_save, sender=Store)
def send_store_created_notification(sender, instance, created, raw, **kwargs):
    """Notify the store owner when their store is successfully created."""

    if created:
        message = NOTIFICATION_TEMPLATES["store_created"][0].format(store_name=instance.store_name)
        Notifications.objects.create(user=instance.store_user, notification_type="store_created", message=message)


# =============================================================================
# STORE MEMBER MILESTONE NOTIFICATION
# =============================================================================

MILESTONE_INTERVAL = 100  # 100, 200, 300, 400...


@receiver(m2m_changed, sender=Store.members.through)
def send_store_member_milestone_notification(
    sender, instance, action, pk_set, **kwargs
):
    """
    Notify the store owner when member count crosses 100, 200, 300, etc.
    Handles bulk adds correctly (e.g. adding 10 members at once).
    """
    if action != "post_add" or not pk_set:
        return

    added_count = len(pk_set)
    current_count = instance.members.count()
    previous_count = current_count - added_count

    # Find every milestone crossed during this add operation
    milestones_reached = []
    milestone = MILESTONE_INTERVAL

    while milestone <= current_count:
        if previous_count < milestone <= current_count:
            milestones_reached.append(milestone)
        milestone += MILESTONE_INTERVAL

    for milestone in milestones_reached:
        message = NOTIFICATION_TEMPLATES["store_milestone_members"][0].format(
            store_name=instance.store_name, milestone=milestone
        )
        Notifications.objects.create(
            user=instance.store_user,
            notification_type="store_milestone_members",
            message=message,
        )
