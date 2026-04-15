from django.shortcuts import render, redirect, get_object_or_404
from core.models import ReturnRequest, OrderItem, OrderStatusHistory
from django.utils import timezone
from django.contrib import messages
from django.db import transaction

def admin_returns(request):
    return_requests = ReturnRequest.objects.all().order_by("-requested_at")
    return render(request, "returns/returns.html", {
        "return_requests": return_requests
    })

def approve_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "APPROVED"
            return_request.approved_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_APPROVED"
            order_item.save()

            # Update timeline
            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_APPROVED"
            )

        messages.success(request, "Return request approved successfully.")
    return redirect("admin-returns")

def reject_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "REJECTED"
            return_request.rejected_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_REJECTED"
            order_item.save()

            # Update timeline
            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_REJECTED"
            )

        messages.error(request, "Return request rejected.")
    return redirect("admin-returns")

def complete_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "COMPLETED"
            # Assuming COMPLETED maps to refund completed in user workflow
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_COMPLETED"
            order_item.save()

            # Update timeline
            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_COMPLETED"
            )

            # Update order payment status if needed
            if return_request.order.payment_status == "PAID":
                return_request.order.payment_status = "REFUNDED"
                return_request.order.save()

        messages.success(request, "Return completed and refund processed.")
    return redirect("admin-returns")
