from django.shortcuts import render
from core.models import Order
def orders_list(request):
    orders = Order.objects.all()
    return render(request, 'order_management/orders_list.html',{
        "orders":orders
    })

def order_detail(request, order_id):
    return render(request, 'order_management/order_detail.html', {'order_id': order_id})

def inventory_list(request):
    return render(request, 'order_management/inventory_list.html')
