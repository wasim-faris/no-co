from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from products.models import Variant
from .models import Cart
from django.contrib import messages
from django.db.models import F,Sum

def cart_view(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        user = request.user
        session = None
    else:
        user = None
        session = session_key

    cart_items = Cart.objects.filter(
        user = user,
        session_key = session
    )


    order_total = Cart.objects.filter(
        user=user,
        session_key = session
    ).aggregate(
        total=Sum(F("price") * F("quantity"))
    )["total"] or 0

    if order_total > 2000:
        delivery_fee = 0
    else:
        delivery_fee = 149

    full_total = delivery_fee + order_total

    return render(request, 'cart.html',{
        "cart_items":cart_items,
        "order_total":order_total,
        "delivery_fee":delivery_fee,
        "full_total":full_total
    })

def add_to_cart(request, variant_id):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        user = request.user
        session = None
    else:
        user = None
        session = session_key

    variant = get_object_or_404(Variant, id=variant_id)

    cart_item = Cart.objects.filter(
        user=user,
        session_key=session,
        variant=variant
    ).first()


    if cart_item:
        cart_item.quantity+=1
        cart_item.save()
    else:
        Cart.objects.create(
            variant = variant,
            user=user,
            session_key = session,
            quantity = 1,
            price = variant.price
        )

    messages.success(request, "Product Added to cart")
    return redirect(request.META.get('HTTP_REFERER'))

def delete_cart_item(request):
    if request.method == "POST":
        cart_id = request.POST.get("cart_id")

        if cart_id:
            if request.user.is_authenticated:
                Cart.objects.filter(id=cart_id , user = request.user).delete()
            else:
                if not request.session.session_key:
                    request.session.create()
                Cart.objects.filter(id=cart_id , session_key = request.session.session_key).delete()

            messages.success(request, "Product delete from cart")
            return redirect("cart")
