from django.http import HttpResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from core.models import Order, OrderStatusHistory
from admin_dashboard.decorators import admin_required
from django.core.exceptions import ValidationError
from accounts.models import ReferralRecord
from wallet.models import Wallet, WalletTransaction
from decimal import Decimal

@admin_required
def orders_list(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    payment_status_filter = request.GET.get('payment_status', '')
    payment_method_filter = request.GET.get('payment_method', '')

    orders = Order.objects.all().order_by("-created_at")

    if search_query:
        from django.db.models import Q
        orders = orders.filter(
            Q(order_number__icontains=search_query.replace('#', '')) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(items__variant__product__product_name__icontains=search_query) |
            Q(items__item_status__icontains=search_query)
        ).distinct()

    if status_filter:
        orders = orders.filter(items__item_status=status_filter).distinct()

    if payment_status_filter:
        orders = orders.filter(payment_status=payment_status_filter)

    if payment_method_filter:
        orders = orders.filter(payment_method=payment_method_filter)

    paginator = Paginator(orders, 4)
    page_number = request.GET.get("page")
    order_obj = paginator.get_page(page_number)

    context = {
        "page_obj": order_obj,
        "orders_count": orders.count(),
        "search_query": search_query,
        "status_filter": status_filter,
        "payment_status_filter": payment_status_filter,
        "payment_method_filter": payment_method_filter,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'order_management/orders_list.html', context)

    return render(request, 'order_management/orders_list.html', context)

@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_management/order_detail.html', {'order_id': order_id, "order":order})

def inventory_list(request):
    return HttpResponse("currenlty unavailable")

def admin_update_order_status(request, order_id):
    if request.method == "POST":
        new_status = request.POST.get("status")
        tracking_id = request.POST.get("tracking_id", "").strip()
        courier_name = request.POST.get("courier_name", "").strip()
        admin_notes = request.POST.get("admin_notes", "").strip()

        order = get_object_or_404(Order, id=order_id)

        valid_statuses = [
            "PENDING",
            "CONFIRMED",
            "PROCESSING",
            "SHIPPED",
            "OUT_FOR_DELIVERY",
            "DELIVERED",
            "CANCELLED",
        ]

        with transaction.atomic():
            if new_status in valid_statuses:
                try:
                    for item in order.items.all():
                        item.item_status = new_status
                        item.clean()
                except ValidationError as e:
                    messages.error(request, e.message)
                    return redirect("admin-order-detail", order_id=order_id)

                for item in order.items.all():
                    item.item_status = new_status
                    item.save()

                last_history = order.status_history.first()
                if not last_history or last_history.status != new_status:
                    OrderStatusHistory.objects.create(
                        order=order,
                        status=new_status,
                    )

                if new_status == "CANCELLED":
                    order.cancelled_at = timezone.now()
                    
                    # Refund logic for prepaid orders (Online or Wallet)
                    # Note: COD orders are only refunded if they were already delivered/paid (which is rare for a cancel, but handled)
                    if order.payment_status == "PAID" or order.payment_method == "wallet":
                        from wallet.models import Wallet, WalletTransaction
                        from decimal import Decimal
                        
                        # Only refund if not already refunded
                        if order.payment_status != "REFUNDED":
                            wallet, _ = Wallet.objects.get_or_create(user=order.user)
                            refund_amount = order.total_amount
                            
                            # Update wallet balance
                            wallet.balance = Decimal(wallet.balance) + Decimal(refund_amount)
                            wallet.save()
                            
                            # Record transaction
                            WalletTransaction.objects.create(
                                wallet=wallet,
                                order_id=order.id,
                                amount=refund_amount,
                                transaction_type='CREDIT',
                                payment_status='SUCCESS',
                                description=f"Refund for Order #{order.order_number} cancelled by administrator"
                            )
                            
                            # Update order payment status
                            order.payment_status = "REFUNDED"
                            order.save()

                if new_status == "DELIVERED":
                    order.delivered_date = timezone.now()
                    
                    # Referral Reward Logic
                    try:
                        # Check if the user who placed the order was referred by someone
                        referral_record = ReferralRecord.objects.get(referred_user=order.user, reward_paid=False)
                        
                        # Use transaction.atomic() to ensure both rewards are processed or none
                        with transaction.atomic():
                            referrer = referral_record.referrer
                            referred_user = order.user
                            
                            # 1. Reward the Referrer (₹100)
                            referrer_wallet, _ = Wallet.objects.get_or_create(user=referrer)
                            reward_referrer = Decimal('100.00')
                            referrer_wallet.balance += reward_referrer
                            referrer_wallet.save()
                            
                            WalletTransaction.objects.create(
                                wallet=referrer_wallet,
                                amount=reward_referrer,
                                transaction_type='CREDIT',
                                payment_status='SUCCESS',
                                description=f"Referral reward — your friend completed their first order"
                            )
                            
                            # 2. Reward the New User (₹40)
                            user_wallet, _ = Wallet.objects.get_or_create(user=referred_user)
                            reward_referred = Decimal('40.00')
                            user_wallet.balance += reward_referred
                            user_wallet.save()
                            
                            WalletTransaction.objects.create(
                                wallet=user_wallet,
                                amount=reward_referred,
                                transaction_type='CREDIT',
                                payment_status='SUCCESS',
                                description=f"Referral bonus — reward for joining with a referral code"
                            )
                            
                            # 3. Mark the referral as paid to prevent duplicates
                            referral_record.reward_paid = True
                            referral_record.save()
                            
                    except ReferralRecord.DoesNotExist:
                        # Either user wasn't referred, or reward already paid
                        pass

            if tracking_id:
                order.tracking_id = tracking_id
            if courier_name:
                order.courier_name = courier_name
            if admin_notes:
                order.admin_notes = admin_notes

            order.save()

        messages.success(request, "Order details updated successfully.")
    return redirect("admin-order-detail", order_id=order_id)
