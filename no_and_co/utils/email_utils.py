"""
NO & CO — Email Utility Functions
Place this file at:  no_and_co/utils/email_utils.py
"""

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


# ─────────────────────────────────────────
# OTP EMAIL
# ─────────────────────────────────────────
def send_otp_email(email: str, otp: str) -> bool:
    """
    Send a luxury OTP verification email.

    Usage:
        from utils.email_utils import send_otp_email
        send_otp_email('user@example.com', '482931')
    """
    subject = "Your NO & CO Verification Code"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    text_body = (
        f"Your NO & CO verification code is: {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"If you did not request this, please ignore this email."
    )
    html_body = render_to_string('emails/otp_email.html', {'otp': otp})

    try:
        msg = EmailMultiAlternatives(subject, text_body, from_email, [email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        print(f"[send_otp_email] Failed for {email}: {exc}")
        return False


# ─────────────────────────────────────────
# FORGOT PASSWORD EMAIL
# ─────────────────────────────────────────
def send_forgot_password_email(user, reset_link: str, expiry_hours: int = 24) -> bool:
    """
    Send a luxury forgot-password / reset-link email.

    Usage (in accounts/views.py):
        from utils.email_utils import send_forgot_password_email
        send_forgot_password_email(user, reset_link='https://yourdomain.com/reset-password/<uid>/<token>/')

    `reset_link` must be the full absolute URL built before calling this function.
    """
    subject = "Reset Your NO & CO Password"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)

    user_name = getattr(user, 'first_name', None) or user.username

    context = {
        'user_name':    user_name,
        'reset_link':   reset_link,
        'expiry_hours': expiry_hours,
    }

    text_body = (
        f"Hi {user_name},\n\n"
        f"We received a request to reset your NO & CO account password.\n\n"
        f"Click the link below (valid for {expiry_hours} hours):\n{reset_link}\n\n"
        f"If you did not request this, please ignore this email — your password won't change.\n\n"
        f"NO & CO"
    )
    html_body = render_to_string('emails/forgot_password_email.html', context)

    try:
        msg = EmailMultiAlternatives(subject, text_body, from_email, [user.email])
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        print(f"[send_forgot_password_email] Failed for {user.email}: {exc}")
        return False



# ─────────────────────────────────────────
# ORDER CONFIRMATION EMAIL
# ─────────────────────────────────────────
def send_order_confirmation_email(order) -> bool:
    """
    Send a luxury order confirmation email.

    Usage:
        from utils.email_utils import send_order_confirmation_email
        send_order_confirmation_email(order_instance)

    The `order` object must be an Order model instance with the
    standard relations: order.items, order.address, order.user.

    Returns True on success, False on failure.
    """
    subject = f"Order Confirmed — #{order.order_number}"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'NO & CO <no-reply@noandco.com>')
    to_email = order.user.email

    # ── Build item list for the template ──────────────────────────
    items = []
    for oi in order.items.select_related('variant__product', 'variant__size').all():
        variant_parts = []
        if oi.variant.color:
            variant_parts.append(oi.variant.color)
        if oi.variant.size:
            variant_parts.append(f"Size {oi.variant.size.name}")

        items.append({
            'name':     oi.variant.product.product_name,
            'variant':  ' · '.join(variant_parts),
            'quantity': oi.quantity,
            'price':    oi.price,
        })

    # ── Shipping address block ─────────────────────────────────────
    addr = order.address
    address_parts = [
        f"{addr.first_name} {addr.last_name}",
        addr.address_line1,
    ]
    if addr.address_line2:
        address_parts.append(addr.address_line2)
    address_parts.append(f"{addr.city}, {addr.state} – {addr.pin_code}")
    address_parts.append(addr.country)
    shipping_address = "\n".join(address_parts)

    # ── Estimated delivery ─────────────────────────────────────────
    from datetime import date, timedelta
    estimated_delivery_date = date.today() + timedelta(days=7)
    estimated_delivery = estimated_delivery_date.strftime("%-d %B %Y")  # e.g. "3 May 2025"
    # Windows fallback (%-d not supported on Windows):
    # estimated_delivery = estimated_delivery_date.strftime("%d %B %Y").lstrip('0')

    # ── Template context ───────────────────────────────────────────
    context = {
        'customer_name':      addr.first_name,
        'order_id':           order.order_number,
        'order_date':         order.created_at.strftime("%d %B %Y"),
        'items':              items,
        'subtotal':           order.active_original_subtotal,
        'shipping':           order.delivery_charge,
        'discount':           order.active_discount if order.active_discount > 0 else None,
        'total':              order.active_total,
        'shipping_address':   shipping_address,
        'estimated_delivery': estimated_delivery,
    }

    # ── Plain-text fallback ────────────────────────────────────────
    item_lines = "\n".join(
        f"  • {i['name']} (x{i['quantity']}) — ₹{i['price']}"
        for i in items
    )
    text_body = (
        f"Hi {context['customer_name']},\n\n"
        f"Your order #{context['order_id']} has been confirmed.\n\n"
        f"Items:\n{item_lines}\n\n"
        f"Subtotal: ₹{context['subtotal']}\n"
        f"Shipping: {'Free' if not context['shipping'] else '₹' + str(context['shipping'])}\n"
        f"Total:    ₹{context['total']}\n\n"
        f"Ship to:\n{shipping_address}\n\n"
        f"Estimated Delivery: {context['estimated_delivery']}\n\n"
        f"Thank you for shopping with NO & CO."
    )

    html_body = render_to_string('emails/order_confirmation_email.html', context)

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=from_email,
            to=[to_email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        print(f"[send_order_confirmation_email] Failed to send to {to_email}: {exc}")
        return False
