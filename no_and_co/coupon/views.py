from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import JsonResponse
import datetime
from admin_dashboard.decorators import admin_required
from django.views.decorators.cache import never_cache
from .models import Coupon, CouponUsage
from django.db.models import Count, Max
from django.core.paginator import Paginator
@admin_required
@never_cache

def admin_coupons(request):
    coupons = Coupon.objects.all().order_by('-created_at')
    status = request.GET.get("status")
    if status == "archived":
        coupons = coupons.filter(is_deleted = True)
    else:
        coupons = coupons.filter(is_active = True , is_deleted = False)

    paginator = Paginator(coupons, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    for coupon in page_obj:
        coupon.used_count = CouponUsage.objects.filter(coupon=coupon).count()
        # Find the highest usage count by any single user
        usage_stats = CouponUsage.objects.filter(coupon=coupon).values('user').annotate(user_usage=Count('id')).aggregate(max_user_usage=Max('user_usage'))
        coupon.max_user_usage = usage_stats['max_user_usage'] or 0

        if coupon.total_usage_limit:
            coupon.usage_display = f"{coupon.used_count}/{coupon.total_usage_limit}"
            coupon.usage_percent = (coupon.used_count / coupon.total_usage_limit) * 100
        else:
            coupon.usage_display = f"{coupon.used_count}/∞"
            coupon.usage_percent = 0

    return render(request, "coupon/admin_coupons.html", {
        "page_obj": page_obj
    })

def add_coupon(request):
    if request.method == "POST":
        print(dict(request.POST))
        code = request.POST.get("code", "").strip()
        discount_value = request.POST.get("discount_value")
        discount_type = request.POST.get("discount_type")
        min_purchase = request.POST.get("min_purchase")
        max_discount = request.POST.get("max_discount")
        usage_limit_per_user = request.POST.get("usage_limit_per_user")
        total_usage_limit = request.POST.get("total_usage_limit")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "true"

        errors = {}
        if not code:
            errors['code'] = 'Coupon code is required.'
        if not discount_value:
            errors['discount_value'] = 'Discount value is required.'
        if not discount_type:
            errors['discount_type'] = 'Discount type is required.'

        if discount_type == 'percentage' and discount_value:
            try:
                val = float(discount_value)
                if val < 1 or val > 100:
                    errors['discount_value'] = 'Discount percentage must be between 1% and 100%.'
            except ValueError:
                errors['discount_value'] = 'Invalid format.'

        if not start_date:
            errors['start_date'] = 'Start date is required.'
        if not end_date:
            errors['end_date'] = 'End date is required.'

        if start_date and end_date:
            try:
                start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                today = datetime.date.today()

                if start < today:
                    errors['start_date'] = 'Start date cannot be in the past.'
                if end < today:
                    errors['end_date'] = 'End date cannot be in the past.'
                elif end < start:
                    errors['end_date'] = 'End date must be later than start date.'
            except ValueError:
                errors['start_date'] = 'Invalid date format.'

        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": errors}, status=400)
            for field, msg in errors.items():
                messages.error(request, f"{field.replace('_', ' ').capitalize()}: {msg}")
            return redirect("admin-coupons")

        Coupon.objects.create(
            code = code,
            discount_type = discount_type,
            discount_value = discount_value,
            min_purchase = min_purchase if min_purchase else 0,
            max_discount = max_discount if max_discount else None,
            total_usage_limit = total_usage_limit if total_usage_limit else None,
            usage_limit_per_user = usage_limit_per_user if usage_limit_per_user else None,
            start_date = start_date,
            end_date = end_date,
            is_active = is_active
        )

        messages.success(request, "Coupon added successfully")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({"success": True})
        return redirect("admin-coupons")

def edit_coupon(request):
    if request.method == "POST":
        print(dict(request.POST))
        coupon_id = request.POST.get("coupon_id")
        code = request.POST.get("code", "").strip()
        discount_value = request.POST.get("discount_value")
        discount_type = request.POST.get("discount_type")
        min_purchase = request.POST.get("min_purchase")
        max_discount = request.POST.get("max_discount")
        usage_limit_per_user = request.POST.get("usage_limit_per_user")
        total_usage_limit = request.POST.get("total_usage_limit")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        is_active = request.POST.get("is_active") == "true"

        errors = {}

        if not code:
            errors['code'] = 'Coupon code is required.'
        if not discount_value:
            errors['discount_value'] = 'Discount value is required.'
        if not discount_type:
            errors['discount_type'] = 'Discount type is required.'

        if discount_type == 'percentage' and discount_value:
            try:
                val = float(discount_value)
                if val < 1 or val > 100:
                    errors['discount_value'] = 'Discount percentage must be between 1% and 100%.'
            except ValueError:
                errors['discount_value'] = 'Invalid format.'

        if not start_date:
            errors['start_date'] = 'Start date is required.'
        if not end_date:
            errors['end_date'] = 'End date is required.'

        if start_date and end_date:
            try:
                start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
                today = datetime.date.today()

                # Check original coupon for Edit logic
                coupon_obj = Coupon.objects.filter(id=coupon_id).first()

                if start < today:
                    if not (coupon_obj and coupon_obj.start_date == start):
                        errors['start_date'] = 'Start date cannot be in the past.'

                if end < today:
                    errors['end_date'] = 'End date cannot be in the past.'
                elif end < start:
                    errors['end_date'] = 'End date must be later than start date.'
            except ValueError:
                errors['start_date'] = 'Invalid date format.'

        if errors:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "errors": errors}, status=400)
            return redirect("admin-coupons")

        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            coupon_obj.code = code
            coupon_obj.discount_type = discount_type
            coupon_obj.discount_value = discount_value
            coupon_obj.min_purchase = min_purchase if min_purchase else 0
            coupon_obj.max_discount = max_discount if max_discount else None
            coupon_obj.usage_limit_per_user = usage_limit_per_user if usage_limit_per_user else None
            coupon_obj.total_usage_limit = total_usage_limit if total_usage_limit else None
            coupon_obj.start_date = start_date
            coupon_obj.end_date = end_date
            coupon_obj.is_active = is_active
            coupon_obj.save()

            messages.success(request, "Coupon edited successfully")
            return JsonResponse({"success": True})

        except Coupon.DoesNotExist:
            return JsonResponse({"success": False, "errors": {"code": "Coupon not found"}}, status=404)

    return redirect("admin-coupons")

def coupon_soft_delete(request):
    if request.method == "POST":
        print(dict(request.POST))
        coupon_id = request.POST.get("coupon_id")

        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            coupon_obj.is_deleted = True
            coupon_obj.is_active = False
            coupon_obj.save()
            messages.success(request, "coupon deleted succesfully")
            return redirect("admin-coupons")

        except Coupon.DoesNotExist:
            messages.error(request, "coupon not found")
            return redirect("admin-coupons")

def coupon_restore(request):
    if request.method == "POST":
        coupon_id = request.POST.get("coupon_id")

        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            coupon_obj.is_deleted = False
            coupon_obj.is_active = True
            coupon_obj.save()
            messages.success(request, "Coupon restored successfully")
            return redirect("admin-coupons")

        except Coupon.DoesNotExist:
            messages.error(request, "Coupon not found")
            return redirect("admin-coupons")
def delete_coupon(request):
    if request.method == "POST":
        coupon_id = request.POST.get("coupon_id")

        try:
            coupon_obj = Coupon.objects.get(id=coupon_id)
            coupon_obj.delete()
            messages.success(request, "coupons deleted permanently")
            return redirect("admin-coupons")
        except Coupon.DoesNotExist:
            messages.success(request, "coupons not found")
            return redirect("admin-coupons")
