from django.shortcuts import render, redirect
import json
from django.shortcuts import get_object_or_404
from products.models import Variant, VariantImage
from .models import Wishlist
from django.contrib import messages
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Prefetch, Sum
from products.models import Variant, VariantImage, Product
from cart.models import Cart
from offers.utils import apply_offers_to_variants


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
        wishlist_items = (
            Wishlist.objects.filter(user=user)
            .select_related("variant")
            .prefetch_related(
                Prefetch(
                    "variant__images",
                    queryset=VariantImage.objects.filter(is_primary=True),
                    to_attr="primary_images",
                )
            )
        )
    else:
        wishlist_items = (
            Wishlist.objects.filter(session_key=session_key)
            .select_related("variant")
            .prefetch_related(
                Prefetch(
                    "variant__images",
                    queryset=VariantImage.objects.filter(is_primary=True),
                    to_attr="primary_images",
                )
            )
        )

    similar_items = []
    if wishlist_items.exists():
        first_product = wishlist_items.first().variant.product
        similar_products = (
            Product.objects.filter(is_active=True, is_deleted=False)
            .exclude(id=first_product.id)
            .order_by("-created_at")[:6]
        )

        for p in similar_products:
            rep_variant = (
                p.variants.filter(is_active=True, is_deleted=False)
                .order_by("-is_default", "id")
                .first()
            )
            if rep_variant:
                similar_items.append(rep_variant)

    similar_items = apply_offers_to_variants(similar_items)
    if not similar_items:
        fallback_products = Product.objects.filter(
            is_active=True, is_deleted=False
        ).order_by("-id")[:8]
        for p in fallback_products:
            rep_variant = (
                p.variants.filter(is_active=True, is_deleted=False)
                .order_by("-is_default", "id")
                .first()
            )
            if rep_variant:
                similar_items.append(rep_variant)
        similar_items = apply_offers_to_variants(similar_items)

    return render(
        request, 
        "wishlist/wishlist.html", 
        {
            "whishlist_items": wishlist_items,
            "similar_items": similar_items,
        }
    )


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
        item = Wishlist.objects.filter(session_key=session_key, variant=variant)

    if item.exists():
        item.delete()
        status = "removed"
    else:
        Wishlist.objects.create(user=user, session_key=session_key, variant=variant)
        status = "added"

    # Calculate updated counts
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).aggregate(total=Sum("quantity"))["total"] or 0
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        cart_count = Cart.objects.filter(session_key=request.session.session_key).aggregate(total=Sum("quantity"))["total"] or 0
        wishlist_count = Wishlist.objects.filter(session_key=request.session.session_key).count()

    return JsonResponse({
        "status": status,
        "cart_count": cart_count,
        "wishlist_count": wishlist_count
    })


def wishlist_add_to_cart(request):
    data = json.loads(request.body)
    variant_id = data.get("variant_id")
    wishlist_id = data.get("wishlist_id")
    print("wishlist_id:", wishlist_id)

    variant = get_object_or_404(Variant, id=variant_id)

    if variant.stock <= 0:
        return JsonResponse({"error": "Out of stock"}, status=400)

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart_item = Cart.objects.filter(user=request.user, variant=variant)
        if cart_item.exists():
            item = cart_item.first()
            if item.quantity >= variant.stock:
                return JsonResponse({"error": "Out of stock"}, status=400)
            item.quantity += 1
            item.save()
            if wishlist_id:
                Wishlist.objects.filter(id=wishlist_id).delete()
        else:
            Cart.objects.create(user=request.user, variant=variant, price=variant.price)
            if wishlist_id:
                Wishlist.objects.filter(id=wishlist_id).delete()
    else:
        cart_item = Cart.objects.filter(
            session_key=request.session.session_key, variant=variant
        )
        if cart_item.exists():
            item = cart_item.first()
            if item.quantity >= variant.stock:
                return JsonResponse({"error": "Out of stock"}, status=400)
            item.quantity += 1
            item.save()
            if wishlist_id:
                Wishlist.objects.filter(id=wishlist_id).delete()
        else:
            Cart.objects.create(
                session_key=request.session.session_key,
                variant=variant,
                price=variant.price,
            )
            if wishlist_id:
                Wishlist.objects.filter(id=wishlist_id).delete()

    # Calculate updated counts
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).aggregate(total=Sum("quantity"))["total"] or 0
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    else:
        cart_count = Cart.objects.filter(session_key=request.session.session_key).aggregate(total=Sum("quantity"))["total"] or 0
        wishlist_count = Wishlist.objects.filter(session_key=request.session.session_key).count()

    return JsonResponse({
        "success": True, 
        "cart_count": cart_count,
        "wishlist_count": wishlist_count
    }, status=200)


def merge_wishlist_item(request, user, old_session_key):
    if not old_session_key:
        return

    guest_item = Wishlist.objects.filter(session_key=old_session_key, user=None)

    print(guest_item)

    for item in guest_item:
        existing_item = Wishlist.objects.filter(user=user, variant=item.variant).first()

        if existing_item:
            item.delete()
        else:
            item.user = user
            item.session_key = None
            item.save()


def get_wishlist_ids(request):
    if request.user.is_authenticated:
        ids = list(Wishlist.objects.filter(user=request.user).values_list('variant_id', flat=True))
    else:
        session_key = request.session.session_key
        if not session_key:
            ids = []
        else:
            ids = list(Wishlist.objects.filter(session_key=session_key).values_list('variant_id', flat=True))
    
    # Convert IDs to strings for consistency with JS
    ids = [str(id) for id in ids]
    
    return JsonResponse({'wishlist_ids': ids})
