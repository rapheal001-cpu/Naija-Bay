import logging
from django.db.models.signals import post_save, pre_save, m2m_changed
from django.dispatch import receiver
from accounts.models import Notifications
from .models import Product
from NaijaBay.utils import NOTIFICATION_TEMPLATES

logger = logging.getLogger(__name__)


# =============================================================================
# PRODUCT CREATED & SOLD NOTIFICATIONS
# =============================================================================

@receiver(pre_save, sender=Product)
def capture_product_old_state(sender, instance, **kwargs):
    """
    Capture the old 'sold' status before the update is written to the DB.
    We attach it to the instance so post_save can compare.
    """

    try:
        old = Product.objects.only("sold").get(pk=instance.pk)
        instance._pre_save_state = {"sold": old.sold}
    except Product.DoesNotExist:
        pass


@receiver(post_save, sender=Product)
def product_notification(sender, instance, created, raw, **kwargs):
    """
    Notify owner when:
      1. A new product is created
      2. An existing product is marked as sold
    """

    # 1. Product created
    if created:
        message = NOTIFICATION_TEMPLATES["product_created"][1].format(product_name=instance.product_name)
        Notifications.objects.create(user=instance.product_user, message=message,notification_type="product_created")

    # 2. Product marked as sold
    if not created:
        if instance.sold:
            message = NOTIFICATION_TEMPLATES["product_sold"][0].format(product_name=instance.product_name)
            Notifications.objects.create(user=instance.product_user, message=message, notification_type="product_sold")


# =============================================================================
# PRODUCT FAVORITE NOTIFICATION
# =============================================================================

@receiver(m2m_changed, sender=Product.favorites.through)
def product_favorite_notification(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Notify the product owner when someone adds their product to favorites.
    Sends one notification per batch (even if multiple users favorite at once).
    """
    if action != "post_add" or reverse or not pk_set:
        return

    try:
        # Just notify once per favoriting action
        favoriter_count = len(pk_set)
        message = NOTIFICATION_TEMPLATES["product_favorite"][0].format(product_name=instance.product_name, count=favoriter_count)
        Notifications.objects.create(user=instance.product_user,message=message, notification_type="product_favorite")
        
    except Exception as e:
        logger.error(
            f"Error in product_favorite_notification for product {instance.id}: {e}",
            exc_info=True,
        )


# =============================================================================
# PRODUCT VIEW MILESTONE NOTIFICATION
# =============================================================================

MILESTONE_INTERVAL = 100  # 100, 200, 300...

@receiver(m2m_changed, sender=Product.views.through)
def product_view_milestone_notification(
    sender, instance, action, reverse, pk_set, **kwargs
):
    """
    Notify the owner when view count crosses 100, 200, 300, etc.
    Correctly handles bulk adds (e.g. 98 → 103 still triggers the 100 milestone).
    """
    if action != "post_add" or reverse or not pk_set:
        return

    try:
        added_count = len(pk_set)
        current_count = instance.views.count()
        previous_count = current_count - added_count

        # Find every milestone crossed during this add operation
        crossed = []
        milestone = MILESTONE_INTERVAL
        while milestone <= current_count:
            if previous_count < milestone <= current_count:
                crossed.append(milestone)
            milestone += MILESTONE_INTERVAL

        for milestone in crossed:
            message = NOTIFICATION_TEMPLATES["product_milestone_views"][0].format(
                product_name=instance.product_name, view_count=milestone
            )
            Notifications.objects.create(
                user=instance.product_user,
                message=message,
                notification_type="product_milestone_views",
            )
            logger.info(
                f"View milestone ({milestone}) notification for user {instance.product_user_id}, "
                f"product {instance.id}"
            )

    except Exception as e:
        logger.error(
            f"Error in product_view_milestone_notification for product {instance.id}: {e}",
            exc_info=True,
        )
