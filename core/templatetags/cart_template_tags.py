from django import template
from core.models import Order

register = template.Library()


@register.filter
def product_count_user(user):
    """
    Returns how many products exists in cart for 1 order
    """
    if not user.is_authenticated:
        return 0
    else:
        order = Order.objects.filter(user=user, is_ordered=False)[0]
        return order.items.count()
