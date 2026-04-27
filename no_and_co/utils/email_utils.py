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
def send_order_confirmation_email(order):
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string
    from datetime import date, timedelta
    
    # Calculate estimated delivery (7 days from now)
    estimated_delivery_date = date.today() + timedelta(days=7)
    estimated_delivery = estimated_delivery_date.strftime("%d %B %Y").lstrip('0')
    
    # Build shipping address string from address ForeignKey
    addr = order.address
    address_parts = [
        f"{addr.first_name} {addr.last_name}",
        addr.address_line1,
    ]
    if addr.address_line2:
        address_parts.append(addr.address_line2)
    address_parts.append(f"{addr.city}, {addr.state} – {addr.pin_code}")
    address_parts.append(addr.country)
    shipping_address_str = "\n".join(address_parts)
    
    # Build items list for template compatibility
    items_data = []
    for oi in order.items.select_related('variant__product', 'variant__size').all():
        variant_desc = ""
        if oi.variant.color and oi.variant.size:
            variant_desc = f"{oi.variant.color} · Size {oi.variant.size.name}"
        elif oi.variant.color:
            variant_desc = oi.variant.color
        elif oi.variant.size:
            variant_desc = f"Size {oi.variant.size.name}"

        items_data.append({
            'name':     oi.variant.product.product_name,
            'variant':  variant_desc,
            'quantity': oi.quantity,
            'price':    oi.price,
        })

    context = {
        'customer_name':      order.user.get_full_name() or order.user.username,
        'order_id':           order.id,
        'order_date':         order.created_at.strftime('%B %d, %Y'),
        'items':              items_data,
        'subtotal':           order.subtotal,
        'shipping':           order.delivery_charge,
        'total':              order.total_amount,
        'shipping_address':   shipping_address_str,
        'estimated_delivery': estimated_delivery,
    }
    
    html_content = render_to_string(
        'emails/order_confirmation_email.html', context
    )
    
    plain_text = f"""
Order Confirmed — #{order.id}

Hi {context['customer_name']},
Your order has been placed successfully.
Order ID: {order.id}
Total: {order.total_amount}
We will notify you when it ships.
"""
    
    msg = EmailMultiAlternatives(
        subject=f'Order Confirmed — #{order.id}',
        body=plain_text,
        from_email='waseemfaris@gmail.com',
        to=[order.user.email],
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)
