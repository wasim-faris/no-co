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

def pickup_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

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

def receive_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

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

def initiate_refund(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "REFUND_INITIATED"
            return_request.refund_status = "INITIATED"
            return_request.refund_initiated_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "REFUND_INITIATED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="REFUND_INITIATED"
            )

        messages.success(request, "Refund initiated.")
    return redirect("admin-returns")

def complete_refund(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "REFUND_COMPLETED"
            return_request.refund_status = "COMPLETED"
            return_request.refunded_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "REFUND_COMPLETED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="REFUND_COMPLETED"
            )

        messages.success(request, "Refund completed.")
    return redirect("admin-returns")

def complete_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "COMPLETED"
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_COMPLETED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_COMPLETED"
            )

        messages.success(request, "Return process completed.")
    return redirect("admin-returns")
