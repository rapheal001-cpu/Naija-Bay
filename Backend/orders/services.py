"""Business logic for carts and orders.

Dependency direction (keeps imports acyclic):
    orders  -> products, accounts
    payments -> orders, products, accounts
    products -> payments.services (only ``expire_boosts_if_due``; payments imports
                Product lazily inside functions)
Prices, totals and stock are ALWAYS read from the database here, never from the client.
"""

import logging
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from accounts.models import Notifications
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem

logger = logging.getLogger(__name__)

MAX_PER_ITEM = 99

# Forward-only transitions a seller may apply to an item of a PAID order.
ITEM_TRANSITIONS = {
    "pending": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered"],
}


def notify(user, notification_type, message):
    if user is None:
        return
    Notifications.objects.create(
        user=user, notification_type=notification_type, message=message
    )


def delivery_fee():
    return Decimal(str(getattr(settings, "DELIVERY_FEE", 0) or 0))


# =============================================================================
# CART
# =============================================================================

def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def cart_items(cart):
    return (
        cart.items.select_related("product", "product__product_user", "cart")
        .prefetch_related("product__images")
        .order_by("-created_at")
    )


def item_issue(item):
    """Why a cart item can't be ordered right now (or None when it can)."""
    product = item.product
    if product.product_user_id == item.cart.user_id:
        return "You cannot buy your own listing."
    if not product.is_purchasable:
        return "This item is no longer available."
    if item.quantity > product.quantity:
        return f"Only {product.quantity} left in stock."
    return None


def cart_totals(items):
    subtotal = Decimal("0.00")
    count = 0
    has_issues = False
    for item in items:
        if item_issue(item) is None:
            subtotal += item.product.price * item.quantity
            count += item.quantity
        else:
            has_issues = True
    fee = delivery_fee() if count else Decimal("0.00")
    return {
        "subtotal": subtotal,
        "delivery_fee": fee,
        "total": subtotal + fee,
        "item_count": count,
        "has_issues": has_issues,
    }


def _clean_quantity(value):
    try:
        quantity = int(value)
    except (TypeError, ValueError):
        raise ValidationError({"quantity": "Quantity must be a whole number."})
    if quantity < 1 or quantity > MAX_PER_ITEM:
        raise ValidationError(
            {"quantity": f"Quantity must be between 1 and {MAX_PER_ITEM}."}
        )
    return quantity


def _clean_product_id(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValidationError({"product_id": "A valid product id is required."})


@transaction.atomic
def add_to_cart(user, product_id, quantity=1):
    quantity = _clean_quantity(quantity)
    product = Product.objects.filter(pk=_clean_product_id(product_id)).first()
    if product is None:
        raise NotFound("Product not found.")
    if product.product_user_id == user.id:
        raise ValidationError({"detail": "You cannot buy your own listing."})
    if not product.is_purchasable:
        raise ValidationError({"detail": "This item is not available for purchase."})

    cart = get_cart(user)
    item = cart.items.filter(product=product).first()
    new_quantity = quantity + (item.quantity if item else 0)
    if new_quantity > product.quantity:
        raise ValidationError(
            {"quantity": f"Only {product.quantity} available in stock."}
        )
    if new_quantity > MAX_PER_ITEM:
        raise ValidationError(
            {"quantity": f"You can order at most {MAX_PER_ITEM} of one item."}
        )

    if item:
        item.quantity = new_quantity
        item.save(update_fields=["quantity", "updated_at"])
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=new_quantity)
    return cart


@transaction.atomic
def set_cart_quantity(user, product_id, quantity):
    quantity = _clean_quantity(quantity)
    cart = get_cart(user)
    item = cart.items.select_related("product").filter(
        product_id=_clean_product_id(product_id)
    ).first()
    if item is None:
        raise NotFound("That item is not in your cart.")
    if quantity > item.product.quantity:
        raise ValidationError(
            {"quantity": f"Only {item.product.quantity} available in stock."}
        )
    item.quantity = quantity
    item.save(update_fields=["quantity", "updated_at"])
    return cart


@transaction.atomic
def remove_cart_item(user, product_id):
    cart = get_cart(user)
    deleted, _ = cart.items.filter(product_id=_clean_product_id(product_id)).delete()
    if not deleted:
        raise NotFound("That item is not in your cart.")
    return cart


@transaction.atomic
def clear_cart(user):
    cart = get_cart(user)
    cart.items.all().delete()
    return cart


# =============================================================================
# ORDERS
# =============================================================================

def _signature(rows):
    return sorted(rows, key=lambda row: (row[0] or 0, row[1]))


@transaction.atomic
def create_order_from_cart(user, shipping):
    """Turn the user's cart into an unpaid order using trusted DB prices."""
    cart = get_cart(user)
    items = list(cart_items(cart))
    if not items:
        raise ValidationError({"detail": "Your cart is empty."})

    problems = []
    for item in items:
        issue = item_issue(item)
        if issue:
            problems.append({"product": item.product.product_name, "issue": issue})
    if problems:
        raise ValidationError(
            {
                "detail": "Some items in your cart can't be ordered. Update your cart and try again.",
                "items": problems,
            }
        )

    subtotal = sum((i.product.price * i.quantity for i in items), Decimal("0.00"))
    fee = delivery_fee()
    wanted = _signature([(i.product_id, i.quantity, i.product.price) for i in items])

    # Never leave duplicate unpaid orders around: reuse an identical one,
    # cancel any other unpaid pending order from this buyer.
    reusable = None
    stale = Order.objects.filter(
        buyer=user, status="pending", payment_status="unpaid"
    ).prefetch_related("items")
    for order in stale:
        existing = _signature(
            [(it.product_id, it.quantity, it.unit_price) for it in order.items.all()]
        )
        if reusable is None and existing == wanted and order.delivery_fee == fee:
            reusable = order
        else:
            order.status = "cancelled"
            order.save(update_fields=["status", "updated_at"])

    if reusable is not None:
        for field, value in shipping.items():
            setattr(reusable, field, value)
        reusable.save()
        return reusable

    order = Order.objects.create(
        reference=Order.generate_reference(),
        buyer=user,
        subtotal=subtotal,
        delivery_fee=fee,
        total=subtotal + fee,
        **shipping,
    )
    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product=i.product,
                seller=i.product.product_user,
                product_name=i.product.product_name,
                product_slug=i.product.product_slug,
                unit_price=i.product.price,
                quantity=i.quantity,
                line_total=i.product.price * i.quantity,
            )
            for i in items
        ]
    )
    return order


def get_buyer_order(user, reference):
    order = Order.objects.filter(reference=reference, buyer=user).first()
    if order is None:
        raise NotFound("Order not found.")
    return order


@transaction.atomic
def cancel_order(user, reference):
    order = Order.objects.select_for_update().filter(reference=reference, buyer=user).first()
    if order is None:
        raise NotFound("Order not found.")
    if order.payment_status != "unpaid" or order.status != "pending":
        raise ValidationError(
            {"detail": "Only unpaid orders can be cancelled. Contact the seller for paid orders."}
        )
    order.status = "cancelled"
    order.save(update_fields=["status", "updated_at"])
    return order


@transaction.atomic
def mark_order_paid(order_id):
    """Called by payments after a gateway-verified success. Idempotent."""
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.payment_status == "paid":
        return order, False

    sellers = {}
    product_ids = []
    for item in order.items.select_related("product", "seller"):
        if item.product_id is None:
            continue
        product = Product.objects.select_for_update().get(pk=item.product_id)
        product_ids.append(product.pk)
        take = min(item.quantity, product.quantity)
        if take < item.quantity:
            # Stock ran out between checkout and payment. Needs manual follow-up/refund.
            logger.warning(
                "Order %s oversold %s: wanted %s, had %s",
                order.reference, product.pk, item.quantity, product.quantity,
            )
        product.quantity -= take
        product.sold_count += item.quantity
        update_fields = ["quantity", "sold_count", "updated_at"]
        if product.quantity == 0:
            product.sold = True
            product.active = False
            update_fields += ["sold", "active"]
        product.save(update_fields=update_fields)
        if item.seller_id:
            sellers[item.seller_id] = item.seller

    order.payment_status = "paid"
    order.paid_at = timezone.now()
    if order.status == "cancelled":
        # Money arrived for an order we had auto-cancelled: honour it.
        order.status = "pending"
    order.save(update_fields=["payment_status", "paid_at", "status", "updated_at"])

    if order.buyer_id:
        CartItem.objects.filter(
            cart__user_id=order.buyer_id, product_id__in=product_ids
        ).delete()
        notify(order.buyer, "order_placed", f"Your payment for order {order.reference} was received.")
    for seller in sellers.values():
        notify(seller, "order_received", f"You have a new paid order ({order.reference}). Prepare it for delivery.")
    return order, True


def recompute_order_status(order):
    statuses = set(order.items.values_list("status", flat=True))
    live = statuses - {"cancelled"}
    if not live:
        new_status = "cancelled"
    elif live == {"delivered"}:
        new_status = "delivered"
    elif live & {"shipped", "delivered"}:
        new_status = "shipped"
    elif "processing" in live:
        new_status = "processing"
    else:
        new_status = "pending"
    if order.status != new_status:
        order.status = new_status
        order.save(update_fields=["status", "updated_at"])
    return order


@transaction.atomic
def update_item_status(seller, item_id, new_status):
    item = (
        OrderItem.objects.select_for_update(of=("self",))
        .select_related("order", "order__buyer")
        .filter(pk=item_id, seller=seller)
        .first()
    )
    if item is None:
        raise NotFound("Order item not found.")
    if item.order.payment_status != "paid":
        raise ValidationError({"detail": "This order has not been paid for yet."})
    if new_status not in ITEM_TRANSITIONS.get(item.status, []):
        raise ValidationError(
            {"status": f"Cannot change an item from '{item.status}' to '{new_status}'."}
        )
    item.status = new_status
    item.save(update_fields=["status", "updated_at"])
    order = recompute_order_status(item.order)
    notify(
        order.buyer,
        "order_update",
        f'"{item.product_name}" in order {order.reference} is now {new_status}.',
    )
    return item
