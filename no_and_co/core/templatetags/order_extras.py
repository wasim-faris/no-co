from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def filter_status(queryset, status_name):
    """Filters the status history queryset for a specific status."""
    if not queryset:
        return None
    return queryset.filter(status=status_name).first()

@register.filter
def is_returned(item):
    """Checks if an item is returned or refunded."""
    return item.item_status in ["RETURNED", "REFUNDED", "RETURN_REFUNDED"]

@register.filter
def get_remaining_total(order):
    """Calculates the updated total after removing returned and cancelled items."""
    active_items = order.items.exclude(item_status__in=["CANCELLED", "RETURNED", "REFUNDED", "RETURN_REFUNDED"])
    
    if not active_items.exists():
        return Decimal("0.00")
    
    # Subtotal after coupon discount
    active_subtotal = sum(item.final_price * item.quantity for item in active_items)
    
    # Original subtotal (for tax calculation)
    active_original_subtotal = sum(item.price * item.quantity for item in active_items)
    
    # Proportional tax
    if order.subtotal > 0:
        tax_rate = order.tax_amount / order.subtotal
        active_tax = (active_original_subtotal * tax_rate).quantize(Decimal('0.01'))
    else:
        active_tax = Decimal('0.00')
        
    return (active_subtotal + active_tax + order.delivery_charge).quantize(Decimal('0.01'))

@register.filter
def get_refunded_total(order):
    """Calculates the total refunded amount (total_amount - remaining_total)."""
    remaining = get_remaining_total(order)
    return (order.total_amount - remaining).quantize(Decimal('0.01'))

@register.filter
def has_returns(order):
    """Checks if any item in the order is returned or refunded."""
    return order.items.filter(item_status__in=["RETURNED", "REFUNDED", "RETURN_REFUNDED"]).exists()

@register.filter
def get_returned_items_total(order):
    """Calculates the total amount for items that are returned/refunded."""
    all_items = order.items.all()
    returned_items = all_items.filter(item_status__in=["RETURNED", "REFUNDED", "RETURN_REFUNDED"])
    
    if not returned_items.exists():
        return Decimal("0.00")
        
    # If all items are returned, return the full order total per user requirement
    if returned_items.count() == all_items.count():
        return order.total_amount
        
    # Partial return calculation: sum final_price * quantity + proportional tax
    base_refund = sum(item.final_price * item.quantity for item in returned_items)
    
    if order.subtotal > 0:
        tax_rate = order.tax_amount / order.subtotal
        refund_tax = sum(item.price * item.quantity * tax_rate for item in returned_items).quantize(Decimal('0.01'))
    else:
        refund_tax = Decimal('0.00')
        
    return (base_refund + refund_tax).quantize(Decimal('0.01'))

@register.filter
def get_item_line_total(item):
    return (item.final_price * item.quantity).quantize(Decimal('0.01'))

@register.filter
def get_item_refund_amount(item, order):
    """Calculates the total refund (base + tax) for a single item."""
    if order.subtotal > 0:
        tax_rate = order.tax_amount / order.subtotal
        item_tax = (item.price * item.quantity * tax_rate).quantize(Decimal('0.01'))
    else:
        item_tax = Decimal('0.00')
    return (item.final_price * item.quantity + item_tax).quantize(Decimal('0.01'))

@register.filter
def is_partially_returned(order):
    returned = order.items.filter(item_status__in=["RETURNED", "REFUNDED", "RETURN_REFUNDED"]).count()
    total = order.items.count()
    return 0 < returned < total

@register.filter
def is_partially_cancelled(order):
    cancelled = order.items.filter(item_status="CANCELLED").count()
    total = order.items.count()
    return 0 < cancelled < total

@register.filter
def get_item_status_display(item):
    status = item.item_status
    if status == 'RETURN_REFUNDED': return 'RETURNED'
    return status.replace('_', ' ')

@register.filter
def get_latest_refund_date(order):
    from core.models import ReturnRequest
    latest_return = ReturnRequest.objects.filter(order=order, status='REFUNDED').order_by('-refunded_at').first()
    return latest_return.refunded_at if latest_return else None

@register.filter
def get_active_subtotal(order):
    active_items = order.items.exclude(item_status__in=["CANCELLED", "RETURNED", "REFUNDED", "RETURN_REFUNDED"])
    return sum(item.final_price * item.quantity for item in active_items)

@register.filter
def get_active_tax(order):
    active_items = order.items.exclude(item_status__in=["CANCELLED", "RETURNED", "REFUNDED", "RETURN_REFUNDED"])
    active_original_subtotal = sum(item.price * item.quantity for item in active_items)
    if order.subtotal > 0:
        tax_rate = order.tax_amount / order.subtotal
        return (active_original_subtotal * tax_rate).quantize(Decimal('0.01'))
    return Decimal('0.00')

@register.filter
def get_returned_items_list(order):
    return order.items.filter(item_status__in=["RETURNED", "REFUNDED", "RETURN_REFUNDED"])
