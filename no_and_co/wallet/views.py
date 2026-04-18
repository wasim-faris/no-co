from decimal import Decimal
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
import razorpay
from .models import Wallet, WalletTransaction

@login_required
def wallet(request):
    """
    Renders the Wallet page with real data from the database.
    """
    wallet_obj, created = Wallet.objects.get_or_create(user=request.user)
    wallet_transaction = WalletTransaction.objects.filter(wallet=wallet_obj).order_by('-created_at')
    
    context = {
        'wallet': wallet_obj,
        'wallet_transaction': wallet_transaction,
    }
    return render(request, 'wallet/wallet.html', context)

@login_required
def create_wallet_order(request):
    """
    Creates a Razorpay order for wallet top-up, matching the pattern in payment app.
    """
    try:
        data = json.loads(request.body)
        amount = int(data.get("amount")) * 100  # Convert to paise
        
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
        
        # Exact same structure as working payment app order creation
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
    """
    Verifies Razorpay payment and updates wallet balance, matching payment app's reliability.
    """
    if request.method != "POST":
        return JsonResponse({"status": "failed"})

    data = json.loads(request.body or "{}")
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        # Verify the signature
        client.utility.verify_payment_signature({
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id': data.get('razorpay_payment_id'),
            'razorpay_signature': data.get('razorpay_signature')
        })

        # Atomic transaction to ensure data integrity, same as working payment app
        with transaction.atomic():
            wallet_obj, _ = Wallet.objects.get_or_create(user=request.user)
            amount = Decimal(data.get("amount"))
            
            # Update balance
            wallet_obj.balance += amount
            wallet_obj.save()

            # Record transaction
            WalletTransaction.objects.create(
                wallet=wallet_obj,
                amount=amount,
                payment_status="SUCCESS",
                description="Wallet Top-up via Razorpay",
                order_id=None
            )

        return JsonResponse({"status": "success"})
    except Exception as e:
        print("WALLET VERIFY ERROR:", e)
        return JsonResponse({"status": "failed", "message": str(e)})
