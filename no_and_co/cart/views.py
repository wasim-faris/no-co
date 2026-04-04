from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from products.models import Variant
from .models import Cart
from django.contrib import messages
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

    return render(request, 'cart.html',{
        "cart_items":cart_items
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


    count = Cart.objects.filter(
        user=user,
        session_key = session_key
    ).count()
    
    messages.success(request, "Product Added to cart")
    return redirect(request.META.get('HTTP_REFERER'))
