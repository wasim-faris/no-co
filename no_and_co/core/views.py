from ctypes import addressof
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import login, logout
from requests import delete
from users.decorators import block_check
from products.models import Variant, VariantImage, Product
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from category.models import Category, Subcategory
from django.db.models import Q
from wishlist.models import Wishlist
from users.models import Addresses
from django.contrib.auth.decorators import login_required
from cart.models import Cart
from django.db.models import Sum
from django.db import transaction
from .models import Order, OrderItem
from django.db.models import F

# Create your views here.


@never_cache
@block_check
def home(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    variants = (
        Variant.objects.filter(
            is_default=True, is_deleted=False, product__is_deleted=False
        )
        .prefetch_related(
            Prefetch(
                "images",
                queryset=VariantImage.objects.filter(is_primary=True),
                to_attr="primary_images",
            )
        )
        .order_by("-created_at")[:6]
    )

    search_history = request.session.get("search_history", [])

    return render(
        request, "index.html", {"variants": variants, "search_history": search_history}
    )


def ladies(request):
    search_history = request.session.get("search_history", [])
    return render(request, "ladies.html", {"search_history": search_history})


def product_details(request, id):
    product = get_object_or_404(Product, id=id)

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        user = request.user
        session_key = None
    else:
        user = None
        session_key = request.session.session_key

    wishlist_items = (
        Wishlist.objects.filter(user=user, session_key=session_key)
        .select_related("variant")
        .prefetch_related(
            Prefetch(
                "variant__images",
                queryset=VariantImage.objects.filter(is_primary=True),
                to_attr="primary_images",
            )
        )
    )
    whishlist_variant_ids = list(wishlist_items.values_list("variant_id", flat=True))

    variants = (
        product.variants.filter(is_active=True, is_deleted=False)
        .prefetch_related(
            Prefetch(
                "images",
                queryset=VariantImage.objects.filter(is_primary=True),
                to_attr="primary_images",
            ),
            "images",
        )
        .order_by("-is_default", "id")
    )

    # Handle explicit variant requested via query param (e.g. from wishlist)
    variant_id = request.GET.get("variant")
    default_variant = None
    if variant_id:
        default_variant = variants.filter(id=variant_id).first()

    if not default_variant:
        default_variant = variants.first()

    unique_variants = []
    seen_colors = set()

    for i in variants:
        if i.color not in seen_colors:
            unique_variants.append(i)
            seen_colors.add(i.color)

    unique_sizes = []
    seen_sizes = set()

    for i in variants:
        size_name = i.size.name

        if size_name not in seen_sizes:
            unique_sizes.append(i)
            seen_sizes.add(size_name)

    similar_products = (
        Product.objects.filter(is_active=True, is_deleted=False)
        .exclude(id=product.id)
        .order_by("-created_at")[:6]
    )
    similar_items = []

    for p in similar_products:
        rep_variant = (
            p.variants.filter(is_active=True, is_deleted=False)
            .order_by("-is_default", "id")
            .first()
        )
        if rep_variant:
            similar_items.append(rep_variant)

    product_image = None

    if default_variant:
        product_image = default_variant.images.filter(is_primary=True).first()
        if not product_image:
            product_image = default_variant.images.first()

    if not product_image:
        v_fallback = variants.first()
        if v_fallback:
            product_image = v_fallback.images.filter(is_primary=True).first()
            if not product_image:
                product_image = v_fallback.images.first()

    search_history = request.session.get("search_history", [])

    return render(
        request,
        "product-details.html",
        {
            "product": product,
            "variants": variants,
            "unique_variants": unique_variants,
            "unique_sizes": unique_sizes,
            "default_variant": default_variant,
            "product_image": product_image,
            "similar_items": similar_items,
            "search_history": search_history,
            "whishlist_items": wishlist_items,
            "whishlist_variant_ids": whishlist_variant_ids,
        },
    )


def product_listing(request):
    sort = request.GET.get("sort")
    subcategory = request.GET.get("subcategory")
    query = request.GET.get("q")
    action = request.GET.get("action")

    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        user = request.user
        session_key = None
    else:
        user = None
        session_key = request.session.session_key

    wishlist_items = (
        Wishlist.objects.filter(user=user, session_key=session_key)
        .select_related("variant")
        .prefetch_related(
            Prefetch(
                "variant__images",
                queryset=VariantImage.objects.filter(is_primary=True),
                to_attr="primary_images",
            )
        )
    )
    whishlist_variant_ids = list(wishlist_items.values_list("variant_id", flat=True))

    if action == "delete_history":

        request.session["search_history"] = []

    variants = Variant.objects.filter(
        product__is_active=True, product__is_deleted=False, is_default=True
    )

    if query:
        history = request.session.get("search_history", [])

        if query in history:
            history.remove(query)

        history.insert(0, query)

        history = history[:5]

        request.session["search_history"] = history

        variants = variants.filter(
            Q(product__product_name__icontains=query)
            | Q(product__description_fit__icontains=query)
        )

    if subcategory:
        subcategory = subcategory.upper()
        sub = get_object_or_404(Subcategory, subcategory_name=subcategory)
        variants = variants.filter(product__subcategory=sub)

    category_ref = request.GET.get("category")
    min_price = request.GET.get("price_min")
    max_price = request.GET.get("price_max")

    if min_price:
        variants = variants.filter(price__gte=min_price)

    if max_price:
        variants = variants.filter(price__lte=max_price)

    if category_ref:
        category_ref = category_ref.upper()
        category = get_object_or_404(Category, category_name=category_ref)
        variants = variants.filter(product__category=category)

    if sort == "newest":
        variants = variants.order_by("-id")
    elif sort == "lowest_price":
        variants = variants.order_by("price")
    elif sort == "highest_price":
        variants = variants.order_by("-price")
    elif sort == "name_asc":
        variants = variants.order_by("product__product_name")
    elif sort == "name_desc":
        variants = variants.order_by("-product__product_name")

    return render(
        request,
        "product-listing.html",
        {
            "variants": variants,
            "query": query,
            "search_history": request.session.get("search_history", []),
            "whishlist_items": wishlist_items,
            "whishlist_variant_ids": whishlist_variant_ids,
        },
    )


def get_variant_sizes(request, variant_id):
    """API: return all same-product/same-color variants so the drawer can list sizes."""
    from django.http import JsonResponse

    variant = get_object_or_404(Variant, id=variant_id)

    same_color_variants = (
        Variant.objects.filter(
            product=variant.product,
            color=variant.color,
            is_active=True,
            is_deleted=False,
        )
        .select_related("size")
        .order_by("id")
    )

    sizes = [
        {"id": v.id, "size": v.size.name, "stock": v.stock} for v in same_color_variants
    ]

    # Resolve image URL
    image_url = None
    primary = variant.images.filter(is_primary=True).first()
    if primary:
        image_url = request.build_absolute_uri(primary.image.url)
    else:
        first_img = variant.images.first()
        if first_img:
            image_url = request.build_absolute_uri(first_img.image.url)

    return JsonResponse(
        {
            "product_name": variant.product.product_name,
            "price": str(variant.price),
            "color": variant.color,
            "image_url": image_url,
            "product_id": variant.product.id,
            "sizes": sizes,
        }
    )


@login_required(login_url="login")
def checkout(request):
    if request.method == "POST":
        address_id = request.POST.get("is_default")

        if address_id:
            try:
                Addresses.objects.filter(user=request.user, is_default=True).update(
                    is_default=False
                )

                Addresses.objects.filter(
                    user=request.user,
                    id=address_id,
                ).update(is_default=True)

                messages.success(request, "address updated")

            except Exception:
                messages.error(request, "somethink went to wrong")

            return redirect("checkout")

    user_address = Addresses.objects.filter(user=request.user).order_by(
        "-is_default", "-id"
    )

    cart_items = Cart.objects.filter(user=request.user).select_related("variant")

    GST_RATE = Decimal("0.12")
    sub_total = sum(item.variant.price * item.quantity for item in cart_items)

    tax_amount = (sub_total * GST_RATE).quantize(Decimal("0.01"))

    discount = Decimal("0.00")

    if sub_total > Decimal("1999.00"):
        delivery_charge = Decimal("149.00")
    else:
        delivery_charge = Decimal("0.00")

    total_cost = sub_total + tax_amount - discount + delivery_charge

    if not cart_items.exists():
        messages.error(request, "add at least one product to checkout")
        return redirect("cart")

    default_address = Addresses.objects.filter(
        user=request.user, is_default=True
    ).first()

    addresses = Addresses.objects.filter(user=request.user)

    return render(
        request,
        "checkout.html",
        {
            "address": user_address,
            "cart_items": cart_items,
            "total_cost": total_cost,
            "delivery_charge": delivery_charge,
            "tax_amount": tax_amount,
            "sub_total": sub_total,
            "default_address": default_address,
            "discount": discount,
        },
    )


@login_required(login_url="login")
def place_order(request):
    if request.method == "POST":
        user = request.user
        payment_method = request.POST.get("payment_method")
        address_id = request.POST.get("address_id")
        address = get_object_or_404(Addresses, id=address_id, user=user)

        payment_status = "PAID" if payment_method == "COD" else "PENDING"

        if not address_id:
            messages.error(request, "Add address to place order")
            return redirect("checkout")

        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            messages.error(request, "no products in the cart")
            return redirect("cart")

        sub_total = sum(item.variant.price * item.quantity for item in cart_items)

        tax_rate = Decimal("0.12")
        tax_amount = sub_total * tax_rate

        delivery_charge = (
            Decimal("149.00") if sub_total > Decimal("1999.00") else Decimal("0.00")
        )
        discount = Decimal("0.00")
        total_amount = sub_total + tax_amount - discount + delivery_charge

        if request.session.get("order_processing"):
            messages.warning(request, "order is already processed")
            return redirect("checkout")
        request.session["order_processing"] = True

        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    address=address,
                    payment_method=payment_method,
                    subtotal=sub_total,
                    tax_amount=tax_amount,
                    delivery_charge=delivery_charge,
                    total_amount=total_amount,
                    payment_status=payment_status,
                    discount_amount=discount,
                )

                for item in cart_items:
                    updated = Variant.objects.filter(
                        id=item.variant.id, stock__gte=item.quantity
                    ).update(stock=F("stock") - item.quantity)

                    if not updated:
                        raise ValueError(
                            f"Insufficient stock for {item.variant.product.name}."
                        )

                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        price=item.variant.price,
                        quantity=item.quantity,
                    )

                cart_items.delete()

            return redirect("order-success")
        finally:
            request.session.pop("order_processing", None)


@login_required(login_url="login")
def order_success(request):
    order = Order.objects.filter(user=request.user).order_by("-created_at").first()
    return render(request, "order_success.html", {"order": order})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Order

