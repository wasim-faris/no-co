from contextlib import redirect_stderr
from email import message
from pyexpat import model
from winreg import REG_QWORD
from django.contrib import messages
from django.shortcuts import render,redirect
from admin_dashboard.decorators import admin_required
from django.views.decorators.cache import never_cache
from .models import Coupon
from django.core.paginator import Paginator
@admin_required
@never_cache

def admin_coupons(request):
    coupons = Coupon.objects.filter(is_deleted=False, is_active = True).order_by('-created_at')

    paginator = Paginator(coupons, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "coupon/admin_coupons.html", {
        "page_obj": page_obj
    })

def add_coupons(request):
    if request.method == "POST":
        print(dict(request.POST))
        code = request.POST.get("code")
        discount_value = request.POST.get("discount_value")
        discount_type = request.POST.get("discount_type")
        min_purchase = request.POST.get("min_purchase")
        max_discount = request.POST.get("max_discount")
        usage_limit_per_user = request.POST.get("usage_limit_per_user")
        total_usage_limit = request.POST.get("total_usage_limit")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "true"


        Coupon.objects.create(
            code = code,
            discount_type = discount_type,
            discount_value = discount_value,
            min_purchase = min_purchase,
            max_discount = max_discount,
            total_usage_limit = total_usage_limit,
            usage_limit_per_user = usage_limit_per_user,
            start_date = start_date,
            end_date = end_date,
            is_active = is_active
        )

        messages.success(
            request, "coupon added successfully"
        )

        return redirect("admin-coupons")
