from email import message
from itertools import product
import re
from tracemalloc import start

from django.shortcuts import render, redirect
from django.http import JsonResponse
from products.models import Product
from category.models import Category
from django.db.models import F
from .models import Offer, OfferCategory, OfferProduct
from django.contrib import messages
def admin_offers(request):
    return render(request, 'admin-offers.html')

def get_products(request):
    products = Product.objects.filter(is_active=True).annotate(name=F('product_name')).values('id', 'name')
    return JsonResponse(list(products), safe=False)

def get_categories(request):
    categories = Category.objects.filter(is_active=True).annotate(name=F('category_name')).values('id', 'name')
    return JsonResponse(list(categories), safe=False)

def create_offer(request):
    if request.method == "POST":
        name = request.POST.get(name)
        apply_to = request.POST.get("apply_to")
        discount_type = request.POST.get("discount_type")
        discount_value = request.POST.get("discount_value")

        min_purchase = request.POST.get("min_purchase") or 0
        max_discount = request.POST.get("max_discount") or 0

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")

        is_active = request.POST.get("is_active") == "on"

        offer = Offer.objects.create(
            name=name,
            apply_to = apply_to,
            discount_type = discount_type,
            discount_value = discount_value,
            min_purchase = min_purchase,
            max_discount = max_discount,
            start_date = start_date,
            end_date = end_date,
            is_active = is_active
        )

        if apply_to == "product":
            product_id = request.POST.get("product_id")

            if product_id:
                OfferProduct.objects.create(
                    offer=offer,
                    product_id = product_id
                )

            offer.min_purchase = 0
            offer.max_discount = None
            offer.save()

        elif apply_to == "category":
            category_id = request.POST.get("category_id")

            if category_id:
                OfferCategory.objects.create(
                    offer = offer,
                    category_id = category_id
                )

        messages.success(request, "offer created successfully ")
        return redirect("admin-offers")

    return redirect("admin-offers")

