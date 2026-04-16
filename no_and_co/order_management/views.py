from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import transaction
from core.models import Order, OrderStatusHistory
from admin_dashboard.decorators import admin_required
from django.core.exceptions import ValidationError
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
    pass

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

                if new_status == "DELIVERED":
                    order.delivered_date = timezone.now()

            if tracking_id:
                order.tracking_id = tracking_id
            if courier_name:
                order.courier_name = courier_name
            if admin_notes:
                order.admin_notes = admin_notes

            order.save()

        messages.success(request, "Order details updated successfully.")
    return redirect("admin-order-detail", order_id=order_id)
