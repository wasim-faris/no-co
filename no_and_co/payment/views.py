import json
from shutil import ExecError
from statistics import quantiles
from turtle import update
from django.db import transaction
from django.http import JsonResponse
from .models import Payment
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.shortcuts import get_object_or_404
from core.models import Order, OrderItem
from cart.models import Cart
from products.models import Variant
from django.db.models import F
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

    razorpay_order = client.order.create(
        {
            "amount": int(order.total_amount * 100),
            "currency": "INR"
        }
    )

    payment, created  = Payment.objects.get_or_create(
        user = request.user,
        razorpay_order_id = razorpay_order["id"],
        defaults={
            "amount": order.total_amount,
            "status": "pending"
        }
    )

    order.payment = payment
    order.save()


    return render(request, "payment.html",{
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order["id"],
        "amount": razorpay_order["amount"],
        "order":order
    })

def verify_payment(request):
    data = json.loads(request.body)

    client = razorpay.Client(
        auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
             "razorpay_payment_id": data["razorpay_payment_id"],
             "razorpay_signature": data["razorpay_signature"]
        })

        with transaction.atomic():
            payment = Payment.objects.get(
                razorpay_order_id = data["razorpay_order_id"]
            )

            if payment.status == "success":
                return JsonResponse({
                    "status": "already_processed"
                })
            payment.razorpay_payment_id = data["razorpay_payment_id"]
            payment.razorpay_signature = data["razorpay_signature"]
            payment.status = "success"
            payment.save()

            order = Order.objects.get(payment = payment)
            order.payment_status = "PAID"
            order.save()

            cart_items = Cart.objects.filter(user = order.user)

            if not cart_items.exists:
                return JsonResponse({
                    "status": "failed"
                })

            for item in cart_items:
                updated = Variant.objects.filter(
                    id=item.variant.id,
                    stock__gte = item.quantity
                ).update(stock =F("stock") - item.quantity)

                if not updated:
                    raise ValueError("stock not avaible")

                OrderItem.objects.create(
                    order = order,
                    variant = item.variant,
                    price = item.variant.price,
                    quantity = item.quantity
                )

            cart_items.delete()

        return JsonResponse({
            "status": "success"
        })
    except Exception as e:
        print(e)
        return JsonResponse({
            "status": "failed",
            "message": str(e)
        })
