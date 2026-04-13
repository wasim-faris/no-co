from django.shortcuts import render
from core.models import Order
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
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
    return render(request, 'order_management/order_detail.html', {'order_id': order_id,
                                                                  "order":order})

def inventory_list(request):
    return render(request, 'order_management/inventory_list.html')
