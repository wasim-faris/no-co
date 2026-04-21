from django.utils import timezone
from coupon.models import CouponUsage
from cart.models import Cart
from decimal import Decimal
from django.db.models import Sum,F

def coupon_validation(coupon, user, cart_total):

    if coupon.is_deleted:
        return False, "Coupon not available"

    if not coupon.is_active:
        return False, "Coupon inactive"

    today = timezone.now().date()

    if coupon.start_date and today < coupon.start_date:
        return False, "Coupon not started yet"

    if coupon.end_date and today > coupon.end_date:
        return False, "Coupon expired"

    if coupon.min_purchase and cart_total < coupon.min_purchase:
        return False, f"Minimum ₹{coupon.min_purchase} required"

    if coupon.usage_limit_per_user:
        used_count = CouponUsage.objects.filter(user=user, coupon=coupon).count()

        if used_count >= coupon.usage_limit_per_user:
            return False, "You have already used this coupon"

    if coupon.total_usage_limit:
        total_used = CouponUsage.objects.filter(coupon=coupon).count()

        if total_used >= coupon.total_usage_limit:
            return False, "Coupon usage limit reached"

    if coupon.discount_type == "PERCENT":
        discount = (cart_total * coupon.discount_value) / 100

        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value

    return True, discount

def get_cart_total(user):

    total = cart_items = Cart.objects.filter(user=user).aggregate(
        total = Sum(F("variant__price") * F("quantity"))
    )["total"]

    return total or 0

