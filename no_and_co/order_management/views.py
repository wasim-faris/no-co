from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from core.models import Order, OrderStatusHistory


def orders_list(request):

    orders = Order.objects.all().order_by("-created_at")

    paginator = Paginator(orders,4)
    page_number = request.GET.get("page")
    order_obj = paginator.get_page(page_number)
    orders_count = Order.objects.count()

    return render(request, 'order_management/orders_list.html',{
        "page_obj":order_obj,
        "orders_count": orders_count
    })

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_management/order_detail.html', {'order_id': order_id, "order":order})

def inventory_list(request):
    return render(request, 'order_management/inventory_list.html')

def admin_update_order_status(request, order_id):
    new_status = request.POST.get("status")

    order = get_object_or_404(Order, id=order_id)
    
    valid_statuses = [
        "PENDING",
        "CONFIRMED",
        "SHIPPED",
        "OUT_FOR_DELIVERY",
        "DELIVERED",
        "CANCELLED",
        "RETURN_REQUESTED",
        "RETURN_APPROVED",
        "RETURN_COMPLETED",
        "RETURN_REJECTED",
    ]

    if new_status not in valid_statuses:
        messages.error(request, "Invalid status selected")
        return redirect("admin-order-detail", order_id=order.id)

    with transaction.atomic():
        order.items.update(item_status=new_status)
        
        OrderStatusHistory.objects.create(
            order=order,
            status=new_status,
        )

        if new_status == "CANCELLED":
            order.cancelled_at = timezone.now()

        if new_status == "DELIVERED":
            order.delivered_date = timezone.now()

        if new_status == "RETURN_COMPLETED":
            order.payment_status = "REFUNDED"

        order.save()

    messages.success(request, f"Order status updated to {new_status}.")
    return redirect("admin-order-detail", order_id=order.id)
