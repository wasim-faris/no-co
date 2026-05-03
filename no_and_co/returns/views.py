
from django.shortcuts import render, redirect, get_object_or_404
from core.models import ReturnRequest, OrderItem, OrderStatusHistory
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from admin_dashboard.decorators import admin_required
from django.core.paginator import Paginator
from wallet.models import Wallet,WalletTransaction
from decimal import Decimal

@admin_required
def admin_returns(request):
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    return_requests_list = ReturnRequest.objects.all().order_by("-requested_at")

    if search_query:
        from django.db.models import Q
        return_requests_list = return_requests_list.filter(
            Q(id__icontains=search_query.replace('#', '')) |
            Q(order__order_number__icontains=search_query.replace('#', '')) |
            Q(customer__username__icontains=search_query) |
            Q(customer__email__icontains=search_query)
        )

    if status_filter:
        return_requests_list = return_requests_list.filter(status=status_filter)

    paginator = Paginator(return_requests_list, 4)
    page_number = request.GET.get('page')
    return_requests = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "returns/returns.html", {
            "page_obj": return_requests,
            "total_returns": return_requests_list.count(),
            "search_query": search_query,
            "status_filter": status_filter
        })

    return render(request, "returns/returns.html", {
        "page_obj": return_requests,
        "total_returns": return_requests_list.count(),
        "search_query": search_query,
        "status_filter": status_filter
    })

@admin_required
def approve_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "REQUESTED":
            messages.error(request, "Invalid status transition.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "APPROVED"
            return_request.approved_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_APPROVED"
            order_item.save()


            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_APPROVED"
            )

        messages.success(request, "Return request approved successfully.")
    return redirect("admin-returns")

@admin_required
def reject_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "REQUESTED":
            messages.error(request, "Only newly requested returns can be rejected.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "REJECTED"
            return_request.rejected_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_REJECTED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_REJECTED"
            )

        messages.error(request, "Return request rejected.")
    return redirect("admin-returns")

@admin_required
def pickup_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "PICKUP_SCHEDULED":
            messages.error(request, "Pickup can only be marked after it is scheduled.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "PICKED_UP"
            return_request.pickup_completed_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_PICKED_UP"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_PICKED_UP"
            )

        messages.success(request, "Item marked as picked up.")
    return redirect("admin-returns")

@admin_required
def schedule_pickup(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "APPROVED":
            messages.error(request, "Pickup can only be scheduled for approved returns.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "PICKUP_SCHEDULED"
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_PICKUP_SCHEDULED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_PICKUP_SCHEDULED"
            )

        messages.success(request, "Pickup scheduled for the return.")
    return redirect("admin-returns")

@admin_required
def receive_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "PICKED_UP":
            messages.error(request, "Item must be picked up before it can be received.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "RECEIVED"
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_RECEIVED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_RECEIVED"
            )

        messages.success(request, "Item marked as received.")
    return redirect("admin-returns")

@admin_required
def inspect_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "RECEIVED":
            messages.error(request, "Item must be received before it can be inspected.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "INSPECTED"
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_INSPECTED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_INSPECTED"
            )

        messages.success(request, "Item marked as inspected.")
    return redirect("admin-returns")

@admin_required
def initiate_refund(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "INSPECTED":
            messages.error(request, "Refund can only be initiated after inspection.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "REFUND_INITIATED"
            return_request.refund_status = "INITIATED"
            return_request.refund_initiated_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_REFUND_INITIATED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_REFUND_INITIATED"
            )

        messages.success(request, "Refund initiated successfully.")
    return redirect("admin-returns")

@admin_required
def complete_refund(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        if return_request.status != "REFUND_INITIATED":
            messages.error(request, "Refund must be initiated before it can be completed.")
            return redirect("admin-returns")

        with transaction.atomic():
            return_request.status = "REFUNDED"
            return_request.refund_status = "COMPLETED"
            return_request.refunded_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_REFUNDED"
            order_item.save()

            variant = order_item.variant
            variant.stock += order_item.quantity
            variant.save()


            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_REFUNDED"
            )

            user = return_request.order.user
            item = return_request.order_item
            order = return_request.order
            
            # Use item's final_price which already includes proportional coupon discount
            item_base_refund = Decimal(item.final_price) * item.quantity
            
            # Calculate proportional tax for this item
            if order.subtotal > 0:
                tax_rate = order.tax_amount / order.subtotal
                item_tax = (Decimal(item.price) * item.quantity * tax_rate).quantize(Decimal('0.01'))
            else:
                item_tax = Decimal('0.00')
                
            amount = item_base_refund + item_tax
            
            wallet , created = Wallet.objects.get_or_create(user=user)

            wallet.balance = Decimal(wallet.balance) + amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                order_id=return_request.order.id,
                amount=amount,
                payment_status="SUCCESS",
                transaction_type="CREDIT",
                description=f"Refund for returned item in Order #{return_request.order.id}"
            )


        messages.success(request, "Refund completed successfully.")
    return redirect("admin-returns")
