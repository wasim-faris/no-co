from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import F, Q
from django.contrib import messages
from django.core.paginator import Paginator
from datetime import datetime

from products.models import Product
from category.models import Category
from .models import Offer, OfferCategory, OfferProduct


def admin_offers(request):
    offers = Offer.objects.all().order_by('-created_at')


    status = request.GET.get('status')
    if status == 'active':
        offers = offers.filter(is_active=True)
    elif status == 'inactive':
        offers = offers.filter(is_active=False)


    offer_type = request.GET.get('type')
    if offer_type == 'product':
        offers = offers.filter(apply_to='product')
    elif offer_type == 'category':
        offers = offers.filter(apply_to='category')

    # Search
    query = request.GET.get('q')
    if query:
        offers = offers.filter(
            Q(name__icontains=query) |
            Q(offerproduct__product__product_name__icontains=query) |
            Q(offercategory__category__category_name__icontains=query)
        ).distinct()


    paginator = Paginator(offers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin-offers.html', {'offers': page_obj})


def get_products(request):
    products = Product.objects.filter(is_active=True).annotate(name=F('product_name')).values('id', 'name')
    return JsonResponse(list(products), safe=False)


def get_categories(request):
    categories = Category.objects.filter(is_active=True).annotate(name=F('category_name')).values('id', 'name')
    return JsonResponse(list(categories), safe=False)


def create_offer(request):
    if request.method == "POST":
        name = request.POST.get("name")
        apply_to = request.POST.get("apply_to")
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")
        min_purchase = request.POST.get("min_purchase") or 0
        max_discount = request.POST.get("max_discount") or None
        if max_discount == "": max_discount = None
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "on"

        if not start_date or not end_date:
            messages.error(request, "Please select valid start and end dates")
            return redirect("admin-offers")

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            if start_dt < today:
                messages.error(request, "Start date cannot be in the past")
                return redirect("admin-offers")
            if end_dt <= start_dt:
                messages.error(request, "End date must be after start date")
                return redirect("admin-offers")
        except ValueError:
            messages.error(request, "Invalid date selection")
            return redirect("admin-offers")

        from decimal import Decimal, ROUND_HALF_UP
        d_val = Decimal(discount_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        offer = Offer.objects.create(
            name=name, apply_to=apply_to, discount_type=discount_type,
            discount_value=d_val, min_purchase=min_purchase,
            max_discount=max_discount, start_date=start_date,
            end_date=end_date, is_active=is_active
        )

        if apply_to == "product":
            product_id = request.POST.get("product_id")
            if product_id:
                OfferProduct.objects.create(offer=offer, product_id=product_id)
            offer.min_purchase = 0
            offer.max_discount = None
            offer.save()

        elif apply_to == "category":
            category_id = request.POST.get("category_id")
            if category_id:
                OfferCategory.objects.create(offer=offer, category_id=category_id)

        messages.success(request, "Offer created successfully")
        return redirect("admin-offers")
    return redirect("admin-offers")


def update_offer(request, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(Offer, id=offer_id)
        offer.name = request.POST.get("name")
        offer.apply_to = request.POST.get("apply_to")
        offer.discount_type = request.POST.get("discount_type")
        from decimal import Decimal, ROUND_HALF_UP
        offer.discount_value = Decimal(request.POST.get("discount_value")).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        offer.min_purchase = request.POST.get("min_purchase") or 0
        max_disc = request.POST.get("max_discount")
        offer.max_discount = max_disc if max_disc else None
        offer.start_date = request.POST.get("start_date")
        offer.end_date = request.POST.get("end_date")
        offer.is_active = request.POST.get("is_active") == "on"

        if not offer.start_date or not offer.end_date:
            messages.error(request, "Please select valid start and end dates")
            return redirect("admin-offers")

        try:
            start_dt = datetime.strptime(offer.start_date, "%Y-%m-%d").date()
            end_dt = datetime.strptime(offer.end_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            if start_dt < today:
                messages.error(request, "Start date cannot be in the past")
                return redirect("admin-offers")
            if end_dt <= start_dt:
                messages.error(request, "End date must be after start date")
                return redirect("admin-offers")
        except ValueError:
            messages.error(request, "Invalid date selection")
            return redirect("admin-offers")

       
        OfferProduct.objects.filter(offer=offer).delete()
        OfferCategory.objects.filter(offer=offer).delete()

        if offer.apply_to == "product":
            product_id = request.POST.get("product_id")
            if product_id:
                OfferProduct.objects.create(offer=offer, product_id=product_id)
            offer.min_purchase = 0
            offer.max_discount = None
        elif offer.apply_to == "category":
            category_id = request.POST.get("category_id")
            if category_id:
                OfferCategory.objects.create(offer=offer, category_id=category_id)

        offer.save()
        messages.success(request, "Offer updated successfully")
        return redirect("admin-offers")
    return redirect("admin-offers")


def delete_offer(request, offer_id):
    if request.method == "POST" or request.method == "DELETE":
        offer = get_object_or_404(Offer, id=offer_id)
        offer.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


def toggle_offer_status(request, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(Offer, id=offer_id)
        offer.is_active = not offer.is_active
        offer.save()
        return JsonResponse({"success": True, "is_active": offer.is_active})
    return JsonResponse({"success": False}, status=400)
