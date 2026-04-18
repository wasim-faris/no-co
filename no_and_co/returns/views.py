from django.shortcuts import render, redirect, get_object_or_404
from core.models import ReturnRequest, OrderItem, OrderStatusHistory
from django.utils import timezone
from django.contrib import messages
from django.db import transaction
from admin_dashboard.decorators import admin_required
from django.core.paginator import Paginator

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

def schedule_pickup(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

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

def inspect_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

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
            order_item.item_status = "RETURN_REFUND_INITIATED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_REFUND_INITIATED"
            )

        messages.success(request, "Refund initiated successfully.")
    return redirect("admin-returns")

def complete_refund(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        with transaction.atomic():
            return_request.status = "REFUNDED"
            return_request.refund_status = "COMPLETED"
            return_request.refunded_at = timezone.now()
            return_request.save()

            order_item = return_request.order_item
            order_item.item_status = "RETURN_REFUNDED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=return_request.order,
                status="RETURN_REFUNDED"
            )

        messages.success(request, "Refund marked as completed.")
    return redirect("admin-returns")
