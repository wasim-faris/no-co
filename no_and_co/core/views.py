from ctypes import addressof
from decimal import Decimal
from venv import create
from winreg import REG_QWORD
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import login, logout
from razorpay import Payment
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
from .models import Order, OrderItem,OrderStatusHistory,ReturnRequest
from django.db.models import F
from io import BytesIO
from django.template.loader import get_template
from django.core.paginator import Paginator
from django.utils import timezone
from xhtml2pdf import pisa
from django.http import JsonResponse
from wallet.models import Wallet, WalletTransaction
from coupon.models import Coupon
from .utils import coupon_validation, get_cart_total
# Create your views here.


@never_cache
@block_check
def home(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    variants = (
        Variant.objects.filter(
            is_default=True, is_deleted=False, product__is_deleted=False, product__category__category_name = "MENS"
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
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")
    variants = ( Variant.objects.filter(
        is_default = True, is_deleted = False, product__is_deleted =False , product__category__category_name = "LADIES"
    ).prefetch_related(
         Prefetch(
                "images",
                queryset=VariantImage.objects.filter(is_primary=True),
                to_attr="primary_images",
            )
    ).order_by("-created_at")[:6]
    )
    search_history = request.session.get("search_history", [])
    return render(request, "ladies.html", {"search_history": search_history, "variants": variants})

def kids(request):
    search_history = request.session.get("search_history", [])
    return render(request, "kids.html", {"search_history": search_history})


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

    paginator = Paginator(variants, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "product-listing.html",
        {
            "variants": page_obj,
            "page_obj": page_obj,
            "query": query,
            "search_history": request.session.get("search_history", []),
            "whishlist_items": wishlist_items,
            "whishlist_variant_ids": whishlist_variant_ids,
        },
    )


def get_variant_sizes(request, variant_id):

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

    discount = request.session.get("discount",0)

    if sub_total < Decimal("999.00"):
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

    wallet = Wallet.objects.filter(user=request.user).first()
    wallet_balance = wallet.balance if wallet else Decimal("0.00")

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
            "wallet_balance": wallet_balance
        },
    )


@login_required(login_url="login")
def place_order(request):
    if request.method == "POST":
        print(dict(request.POST))
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
            Decimal("149.00") if sub_total < Decimal("999.00") else Decimal("0.00")
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

                OrderStatusHistory.objects.create(
                    order = order,
                    status = "PENDING",
                    updated_at = timezone.now()
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        price=item.variant.price,
                        quantity=item.quantity,
                    )

                if payment_method == "COD":
                    for item in cart_items:
                        updated = Variant.objects.filter(
                            id=item.variant.id, stock__gte=item.quantity
                        ).update(stock=F("stock") - item.quantity)

                        if not updated:
                            raise ValueError(
                                f"Insufficient stock for {item.variant.product.name}."
                            )
                    cart_items.delete()
                    request.session['last_order_id'] = order.id
                    return redirect("order-success")

                if payment_method == "wallet":

                    wallet = Wallet.objects.filter(user=request.user).first()

                    if wallet.balance >= total_amount:
                        wallet.balance = wallet.balance - total_amount
                        wallet.save()


                        WalletTransaction.objects.create(
                            wallet=wallet,
                            order_id=order.id,
                            amount=total_amount,
                            payment_status="SUCCESS",
                            transaction_type="DEBIT",
                            description=f"Payment for Order #{order.id}"
                        )

                        for item in cart_items:
                            updated = Variant.objects.filter(
                                id = item.variant.id, stock__gte=item.quantity
                            ).update(stock=F("stock") - item.quantity)

                            if not updated:
                                raise ValueError(
                                f"Insufficient stock for {item.variant.product.name}."
                                )
                            cart_items.delete()
                            request.session['last_order_id'] = order.id
                            return redirect("order-success")

                    else:
                        messages.error(request, "insufficent money in wallet")
                        return redirect("checkout")

                return redirect("payment-page", order_id=order.id)


        finally:
            request.session.pop("order_processing", None)


@login_required(login_url="login")
def order_success(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('home')


    order = get_object_or_404(Order, id=order_id, user=request.user)


    # Optional: Clear it after one view to prevent refresh access
    del request.session['last_order_id']


    return render(request, "order_success.html", {"order": order})


@login_required(login_url="login")
def orders(request):
    search_query = request.GET.get("search", "").strip()

    orders_list = Order.objects.filter(user=request.user)

    if search_query:
        orders_list = orders_list.filter(
            Q(order_number__icontains=search_query) |
            Q(address__first_name__icontains=search_query) |
            Q(address__last_name__icontains=search_query) |
            Q(payment_method__icontains=search_query) |
            Q(items__item_status__icontains=search_query) |
            Q(items__variant__product__product_name__icontains=search_query) |
            Q(created_at__icontains=search_query)
        ).distinct()


    orders_list = orders_list.order_by('-created_at', '-id').prefetch_related(
        'items', 'items__variant', 'items__variant__product',
        'items__variant__size', 'items__variant__images'
    )


    paginator = Paginator(orders_list, 4)
    page_number = request.GET.get('page')
    orders_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'partials/orders_list_partial.html', {
            'orders': orders_obj
        })

    return render(request, 'orders.html', {
        'orders': orders_obj
    })

@login_required(login_url="login")
def order_details(request, id):

    order = get_object_or_404(Order, user=request.user ,id=id)

    return render(request, 'order_details.html',{
        "order":order
    })


@login_required(login_url="login")
def download_invoice(request, id):

    order = get_object_or_404(Order, user=request.user, id=id)

    items = list(
        order.items.select_related("variant__product", "variant__size").all()
    )
    for item in items:
        item.line_total = item.price * item.quantity

    context = {
        "order": order,
        "items": items,
        "is_pdf": False,
    }

    try:
        context["is_pdf"] = True
        template = get_template("invoice/invoice_template.html")
        html_string = template.render(context)

        buffer = BytesIO()
        pdf_result = pisa.pisaDocument(
            BytesIO(html_string.encode("UTF-8")), buffer
        )

        if not pdf_result.err:
            filename = f"NO-CO-Invoice-{order.order_number}.pdf"
            response = HttpResponse(
                buffer.getvalue(), content_type="application/pdf"
            )
            response["Content-Disposition"] = (
                f'attachment; filename="{filename}"'
            )
            return response

    except ImportError:
        pass

    context["is_pdf"] = False
    return render(request, "invoice/invoice_template.html", context)

@login_required(login_url="login")
@transaction.atomic
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        if order.cancelled_at:
            messages.info(request, "This order has already been cancelled.")
            return redirect("order_details", id=order_id)

        if order.items.filter(item_status__in=["SHIPPED", "DELIVERED"]).exists():
            messages.error(request, "This order cannot be cancelled as it has already been shipped.")
            return redirect("order_details", id=order_id)

        # Restore stock only for items that weren't already cancelled
        items_to_cancel = order.items.select_related("variant").exclude(item_status="CANCELLED")
        for item in items_to_cancel:
            variant = item.variant
            print(variant.stock)
            variant.stock += item.quantity
            print(variant.stock)
            variant.save()

        order.items.update(item_status="CANCELLED")
        OrderStatusHistory.objects.create(
            order=order,
            status="CANCELLED",
            updated_at=timezone.now()
        )
        order.cancelled_at = timezone.now()

        # Handle Refund for prepaid orders
        if order.payment_method in ["ONLINE", "wallet"]:
            wallet, _ = Wallet.objects.get_or_create(user=order.user)
            amount = Decimal(order.total_amount)

            wallet.balance = F('balance') + amount
            wallet.save()

            WalletTransaction.objects.create(
                wallet=wallet,
                order_id=order.id,
                amount=amount,
                payment_status="SUCCESS",
                transaction_type="CREDIT",
                description=f"Refund for cancelled Order #{order.id}"
            )

    if order.payment_method == "ONLINE" and order.payment_status == "PAID":
        order.payment_status = "REFUNDED"
        order.save()
        messages.success(request, "Order cancelled successfully and refund processed.")
    return redirect("order_details", id=order_id)


def return_order(request, order_id):

    order = get_object_or_404(Order, id=order_id , user=request.user)

    if request.method == "POST":
        reason = request.POST.get("return_reason", "").strip()
        description = request.POST.get("return_description", "").strip()
        order_item_id = request.POST.get("order_item_id", "").strip()

        if not all([reason, description, order_item_id]):
            messages.error(request, "All fields are required")
            return redirect("order_details", id=order.id)

        order_item = get_object_or_404(OrderItem, id=order_item_id, order=order)

        if order_item.item_status != "DELIVERED":
            messages.error(request, "Only delivered items can be returned")
            return redirect("order_details", id=order.id)

        with transaction.atomic():
            ReturnRequest.objects.create(
                order=order,
                order_item=order_item,
                customer=request.user,
                reason=reason,
                description=description,
                status="REQUESTED",
                requested_at=timezone.now()
            )

            order_item.item_status = "RETURN_REQUESTED"
            order_item.save()

            OrderStatusHistory.objects.create(
                order=order,
                status="RETURN_REQUESTED"
            )

        messages.success(request, "Return request submitted successfully")
        return redirect("order_details", id=order.id)

def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code")

        try:
            coupon = Coupon.objects.get(code__iexact = code , is_deleted = False , is_active = True)

        except Coupon.DoesNotExist:
            return JsonResponse({
                "success": False , "message": "invalid coupon"
            })
        cart_total = get_cart_total(request.user)

        is_valid, result = coupon_validation(coupon, request.user, cart_total)

        if not is_valid:
            return JsonResponse({
                "success": False , "message": result
            })
        request.session["coupon_id"] = coupon.id
        request.session["discount"] = float(result)

        return JsonResponse({
            "success": True,
            "discount": float(result),
            "messages": "Coupon applied successfully"
        })
