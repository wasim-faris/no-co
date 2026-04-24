from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from products.models import Variant, Product
from .models import Cart
from django.contrib import messages
from django.db.models import F, Sum
from django.http import JsonResponse


def cart_view(request):

    if request.method == "POST":
        action = request.POST.get("action")
        cart_id = request.POST.get("cart_id")

        if not request.session.session_key:
            request.session.create()

        if action in ["increase", "decrease"] and cart_id:
            cart_obj = get_object_or_404(
                Cart,
                id=cart_id,
                user=request.user if request.user.is_authenticated else None,
                session_key=(
                    None
                    if request.user.is_authenticated
                    else request.session.session_key
                ),
            )

            if action == "decrease" and cart_obj.quantity > 1:
                cart_obj.quantity -= 1
                cart_obj.save()
            elif action == "increase":
                if cart_obj.quantity >= 5:
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {"error": "Maximum quantity of 5 reached"}, status=400
                        )
                    return redirect("cart")

                if cart_obj.quantity < cart_obj.variant.stock:
                    cart_obj.quantity += 1
                    cart_obj.save()
                else:
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {"error": f"Only {cart_obj.variant.stock} items available"},
                            status=400,
                        )
                    return redirect("cart")

            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                user = request.user if request.user.is_authenticated else None
                if not request.session.session_key:
                    request.session.create()

                session = (
                    None
                    if request.user.is_authenticated
                    else request.session.session_key
                )

                order_total = (
                    Cart.objects.filter(user=user, session_key=session).aggregate(
                        total=Sum(F("price") * F("quantity"))
                    )["total"]
                    or 0
                )

                cart_count = (
                    Cart.objects.filter(user=user, session_key=session).aggregate(
                        total=Sum("quantity")
                    )["total"]
                    or 0
                )

                delivery_fee = 149 if order_total < 999 else 0
                full_total = delivery_fee + order_total
                item_total = cart_obj.price * cart_obj.quantity

                return JsonResponse(
                    {
                        "quantity": cart_obj.quantity,
                        "item_total": item_total,
                        "order_total": order_total,
                        "full_total": full_total,
                        "delivery_fee": delivery_fee,
                        "cart_count": cart_count,
                    }
                )

            return redirect("cart")

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    if request.user.is_authenticated:
        user = request.user
        session = None
    else:
        user = None
        session = session_key

    cart_items = Cart.objects.filter(user=user, session_key=session).prefetch_related(
        "variant__images"
    ).order_by("-created_at")
    from offers.utils import get_best_offer, apply_offers_to_variants
    for item in cart_items:
        # We need to know the current original price and the best offer 
        # to show the H&M style discount in the cart.
        original_price = item.variant.price
        _, discount_amount = get_best_offer(item.variant.product, original_price)
        
        item.original_price = original_price
        item.final_price = original_price - discount_amount
        item.discount_amount = discount_amount
        item.has_discount = discount_amount > 0
        if original_price > 0:
            item.discount_percent = int((discount_amount / original_price) * 100)
        else:
            item.discount_percent = 0

        # Sync the cart price with the current best price if it changed
        if item.price != item.final_price:
            item.price = item.final_price
            item.save()

        item.total_price = item.price * item.quantity
        images = list(item.variant.images.all())
        primary_img = next((img for img in images if img.is_primary), None)
        item.primary_image = (
            primary_img if primary_img else (images[0] if images else None)
        )

    order_total = (
        Cart.objects.filter(user=user, session_key=session).aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"]
        or 0
    )

    if order_total < 999:
        delivery_fee = 149
    else:
        delivery_fee = 0

    full_total = delivery_fee + order_total

    similar_items = []
    if cart_items.exists():
        first_product = cart_items.first().variant.product
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

    search_history = request.session.get("search_history", [])

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "order_total": order_total,
            "delivery_fee": delivery_fee,
            "full_total": full_total,
            "similar_items": similar_items,
            "search_history": search_history,
        },
    )


def add_to_cart(request, variant_id):
    if request.method != "POST":
        return redirect(request.META.get("HTTP_REFERER", "/"))

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

    from offers.utils import get_best_offer
    _, discount_amount = get_best_offer(variant.product, variant.price)
    final_price = variant.price - discount_amount

    cart_item = Cart.objects.filter(
        user=user, session_key=session, variant=variant
    ).first()

    if cart_item:
        if cart_item.quantity >= 5:
            return JsonResponse(
                {"error": "Maximum quantity of 5 reached per item"}, status=400
            )

        if cart_item.quantity < variant.stock:
            cart_item.quantity += 1
            cart_item.price = final_price # Ensure price is updated if offer changed
            cart_item.save()
        else:
            return JsonResponse(
                {"error": f"Only {variant.stock} items available"}, status=400
            )
    else:
        if variant.stock > 0:
            Cart.objects.create(
                variant=variant,
                user=user,
                session_key=session,
                quantity=1,
                price=final_price,
            )
        else:
            return JsonResponse({"error": "Out of stock"}, status=400)

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        cart_count = (
            Cart.objects.filter(user=user, session_key=session).aggregate(
                total=Sum("quantity")
            )["total"]
            or 0
        )

        cart_count = cart_count or 0
        return JsonResponse({"success": True, "cart_count": cart_count})

    return redirect(request.META.get("HTTP_REFERER", "/"))


def delete_cart_item(request):
    if request.method == "POST":
        cart_id = request.POST.get("cart_id")
        if cart_id:
            if request.user.is_authenticated:
                Cart.objects.filter(id=cart_id, user=request.user).delete()
            else:
                if not request.session.session_key:
                    request.session.create()
                Cart.objects.filter(
                    id=cart_id, session_key=request.session.session_key
                ).delete()

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                user = request.user if request.user.is_authenticated else None
                session = (
                    None
                    if request.user.is_authenticated
                    else request.session.session_key
                )

                order_total = (
                    Cart.objects.filter(user=user, session_key=session).aggregate(
                        total=Sum(F("price") * F("quantity"))
                    )["total"]
                    or 0
                )

                delivery_fee = 149 if order_total < 999 else 0
                full_total = delivery_fee + order_total
                cart_count = (
                    Cart.objects.filter(user=user).aggregate(total=Sum("quantity"))[
                        "total"
                    ]
                    if user
                    else Cart.objects.filter(session_key=session).aggregate(
                        total=Sum("quantity")
                    )["total"]
                )
                cart_count = cart_count or 0

                return JsonResponse(
                    {
                        "success": True,
                        "order_total": order_total,
                        "full_total": full_total,
                        "delivery_fee": delivery_fee,
                        "cart_count": cart_count,
                    }
                )

            messages.success(request, "Product deleted from cart")
            return redirect("cart")


def merge_cart_after_login(request, user, old_session_key):

    if not old_session_key:
        return

    print("MERGE FUNCTION CALLED")
    session_key = request.session.session_key

    if not session_key:
        return

    guest_items = Cart.objects.filter(session_key=old_session_key, user=None)

    print("Guest items:", guest_items)

    for item in guest_items:
        existing_item = Cart.objects.filter(user=user, variant=item.variant).first()

        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.save()
            item.delete()
        else:
            item.user = user
            item.session_key = None
            item.save()
