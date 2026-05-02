from decimal import Decimal
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
import razorpay
from .models import Wallet, WalletTransaction
from django.core.paginator import Paginator

@login_required
def wallet(request):

    wallet_obj, created = Wallet.objects.get_or_create(user=request.user)
    wallet_transaction = WalletTransaction.objects.filter(wallet=wallet_obj).order_by('-created_at')
    paginator = Paginator(wallet_transaction, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        'wallet': wallet_obj,
        "page_obj":page_obj
    }
    return render(request, 'wallet/wallet.html', context)

@login_required
def create_wallet_order(request):

    try:
        data = json.loads(request.body)
        amount = int(data.get("amount")) * 100

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR"
        })

        return JsonResponse({
            "order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "key": settings.RAZORPAY_KEY_ID
        })
    except Exception as e:
        return JsonResponse({"status": "failed", "message": str(e)}, status=400)

@login_required
def verify_wallet_payment(request):

    if request.method != "POST":
        return JsonResponse({"status": "failed"})

    data = json.loads(request.body or "{}")
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        })


        with transaction.atomic():
            wallet_obj, _ = Wallet.objects.get_or_create(user=request.user)
            amount = Decimal(data.get("amount"))

            wallet_obj.balance += amount
            wallet_obj.save()

            WalletTransaction.objects.create(
                wallet=wallet_obj,
                amount=amount,
                payment_status="SUCCESS",
                transaction_type="CREDIT",
                description="Wallet Top-up via Razorpay",
                order_id=None
            )

        return JsonResponse({"status": "success"})
    except Exception as e:
        print("WALLET VERIFY ERROR:", e)
        return JsonResponse({"status": "failed", "message": str(e)})
