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
                order.items.update(item_status=new_status)
                
                # Only create history if status actually changed
                last_history = order.status_history.first()
                if not last_history or last_history.status != new_status:
                    OrderStatusHistory.objects.create(
                        order=order,
                        status=new_status,
                    )

                if new_status == "CANCELLED":
                    order.cancelled_at = timezone.now()

                if new_status == "DELIVERED":
                    order.delivered_date = timezone.now()

            # Always update these fields if provided or changed
            if tracking_id:
                order.tracking_id = tracking_id
            if courier_name:
                order.courier_name = courier_name
            if admin_notes:
                order.admin_notes = admin_notes
                
            order.save()

        messages.success(request, "Order details updated successfully.")
    return redirect("admin-order-detail", order_id=order_id)
