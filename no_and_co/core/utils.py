from django.utils import timezone
from coupon.models import Coupon, CouponUsage
from cart.models import Cart
from decimal import Decimal
from django.db.models import Sum,F

from django.utils import timezone
from coupon.models import CouponUsage

def coupon_validation(coupon, user, cart_total):
    print("USER:", user)
    print("COUPON:", coupon.code)
    print("USED COUNT:", CouponUsage.objects.filter(user=user, coupon=coupon).count())
    print("LIMIT:", coupon.usage_limit_per_user)
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

    # ✅ STRICT PER USER LIMIT (REQUIRED)
    if coupon.usage_limit_per_user is None:
        return False, "This coupon is not valid"

    used_count = CouponUsage.objects.filter(
        user=user,
        coupon=coupon
    ).count()

    if used_count >= coupon.usage_limit_per_user:
        return False, "You have already used this coupon"

    # ✅ EXTRA SAFETY
    if cart_total <= 0:
        return False, "Invalid cart total"

    # ✅ TOTAL LIMIT (CORRECT)
    if coupon.total_usage_limit:
        total_used = CouponUsage.objects.filter(coupon=coupon).count()

        if total_used >= coupon.total_usage_limit:
            return False, "Coupon usage limit reached"

    # ✅ DISCOUNT LOGIC
    if coupon.discount_type == "percentage":
        discount = (cart_total * coupon.discount_value) / 100

        if coupon.max_discount:
            discount = min(discount, coupon.max_discount)
    else:
        discount = coupon.discount_value

    # 🔥 CRITICAL FIX: Discount cannot exceed cart total
    discount = min(discount, cart_total)

    return True, discount

def get_cart_total(user):

    total = cart_items = Cart.objects.filter(user=user).aggregate(
        total = Sum(F("variant__price") * F("quantity"))
    )["total"]

    return total or 0

def get_available_coupons(user, cart_total):
    today = timezone.now().date()

    coupons = Coupon.objects.filter(
        is_active = True,
        is_deleted = False,
        start_date__lte=today,
        end_date__gte = today
    ).order_by("-created_at")

    valid_coupons = []

    for coupon in coupons:
        if coupon.min_purchase and cart_total < coupon.min_purchase:
            continue

        # STRICT RULE: Must have a limit
        if coupon.usage_limit_per_user is None:
            continue

        used = CouponUsage.objects.filter(
            user=user, coupon=coupon
        ).count()

        if used >= coupon.usage_limit_per_user:
            continue

        valid_coupons.append(coupon)

    return valid_coupons
