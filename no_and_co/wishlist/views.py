from django.shortcuts import render,redirect
import json
from django.shortcuts import get_object_or_404
from products.models import Variant,VariantImage
from .models import Wishlist
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Prefetch
from cart.models import Cart
def wishlist(request):

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        user = request.user
        session_key = None
    else:
        user = None
        session_key = request.session.session_key



    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=user).select_related("variant").prefetch_related(
            Prefetch(
                "variant__images",
                queryset=VariantImage.objects.filter(is_primary = True),
                to_attr="primary_images"
            )
        )
    else:
         wishlist_items = Wishlist.objects.filter(session_key=session_key).select_related("variant").prefetch_related(
            Prefetch(
                "variant__images",
                queryset=VariantImage.objects.filter(is_primary = True),
                to_attr="primary_images"
            )
        )


    return render(request, 'wishlist/wishlist.html', {
        "whishlist_items":wishlist_items
    })


def wishlist_toggle(request):

    data = json.loads(request.body)
    variant_id = data.get("variant_id")

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        user = request.user
        session_key = None
    else:
        user = None
        session_key = request.session.session_key

    variant = get_object_or_404(Variant, id=variant_id)

    if request.user.is_authenticated:
        item = Wishlist.objects.filter(user=user, variant=variant)
    else:
        item = Wishlist.objects.filter(session_key = session_key, variant=variant)

    if item.exists():
        item.delete()

        return JsonResponse({
        "status": "removed"
        })

    else:
        Wishlist.objects.create(
            user = user,
            session_key = session_key,
            variant = variant
        )
        return JsonResponse({
        "status": "added"
        })

def wishlist_add_to_cart(request):
    data = json.loads(request.body)
    variant_id = data.get("variant_id")

    variant = get_object_or_404(Variant, id=variant_id)

    if variant.stock <=0:
        return JsonResponse({
            "error":"out of stock"
        })

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user = request.user, variant=variant)
        if cart_item.exists():
            item = cart_item.first()
            if item.quantity >= variant.stock:
                return JsonResponse({
                    "error":"out of stock"
                })
            item.quantity+=1
            item.save()
        else:
            Cart.objects.create(
                user = request.user,
                variant=variant,
                price = variant.price
            )
    else:
        cart_item = Cart.objects.filter(session_key = request.session.session_key , variant = variant)
        if cart_item.exists():
            item = cart_item.first()
            if item.quantity >= variant.stock:
                return JsonResponse({
                    "error":"out of stock"
                })
            item.quantity +=1
            item.save()
        else:
            Cart.objects.create(
                session_key = request.session.session_key,
                variant = variant,
                price = variant.price
            )
    return JsonResponse({
    "success": True
        })

#     else:
#         user = None
#         session_key = request.session.session_key

#     if request.user.is_authenticated:
#         cart_item = Cart.objects.filter(user = user , variant=variant)
#         if cart_item.exists():
#             item = cart_item.first()
#             if item.quantity >= variant.stock:
#                 return JsonResponse({
#                 "error": "No more stock available"
#                         })
#             item.quantity +=1
#             item.save()
#         else:
#             Cart.objects.create(
#                 user = user,
#                 price = variant.price,
#                 variant = variant
#             )
#     else:
#         cart_item = Cart.objects.filter(session_key = session_key, variant = variant)
#         if cart_item.exists():
#             item = cart_item.first()
#             if item.quantity >= variant.stock:
#                 return JsonResponse({
#                 "error": "No more stock available"
#                 })
#             item.quantity +=1
#             item.save()
#         else:
#             Cart.objects.create(
#                 session_key = session_key,
#                 variant = variant,
#                 price = variant.price
#             )
#     return JsonResponse({
#     "success": True
# })
