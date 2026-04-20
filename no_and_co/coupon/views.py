from django.shortcuts import render
from admin_dashboard.decorators import admin_required
from django.views.decorators.cache import never_cache

@admin_required
@never_cache
def admin_coupons(request):
    return render(request, "coupon/admin_coupons.html")
