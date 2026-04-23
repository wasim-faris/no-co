from django.shortcuts import render, redirect
from accounts.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
import random
from django.core.mail import send_mail
import time
import re
from django.contrib.auth.hashers import make_password, check_password
from .decorators import admin_required

email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
password_pattern = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)
from django.views.decorators.cache import never_cache
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta, datetime
import csv
from django.http import HttpResponse

# Create your views here.


def no_cache(response):
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@never_cache
def admin_login(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)

        if user and user.is_superuser:
            login(request, user)
            messages.success(request, "admin login succesfully")
            return redirect("admin-dashboard")
        else:
            if user:
                messages.error(request, "user are not allowed")
                return redirect("login")
            messages.error(request, "invalid username or password")
            return redirect("admin-login")
    return render(request, "account/admin-login.html")


@admin_required
@never_cache
def admin_dashboard(request):
    from core.models import Order, OrderItem
    from django.db.models import Sum, Count, F, Q, Case, When, DecimalField
    from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
    from django.utils import timezone
    from decimal import Decimal
    import datetime
    import csv
    from django.http import JsonResponse, HttpResponse
    from django.template.loader import get_template
    from io import BytesIO

    filter_type = request.GET.get('filter', 'daily')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    chart_filter = request.GET.get('chart_filter', 'monthly')
    download_format = request.GET.get('download')

    now = timezone.now()
    
    # Use subquery to avoid JOIN duplication during aggregation
    valid_order_ids = Order.objects.filter(
        Q(payment_status='PAID') | 
        Q(payment_method='COD', items__item_status='DELIVERED')
    ).values('id')

    valid_orders = Order.objects.filter(id__in=valid_order_ids)

    if filter_type == 'daily':
        start = now - datetime.timedelta(days=7)
        orders = valid_orders.filter(created_at__gte=start)
    elif filter_type == 'weekly':
        start = now - datetime.timedelta(weeks=12)
        orders = valid_orders.filter(created_at__gte=start)
    elif filter_type == 'yearly':
        start = now.replace(year=now.year - 5)
        orders = valid_orders.filter(created_at__gte=start)
    elif filter_type == 'custom' and start_date and end_date:
        s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        orders = valid_orders.filter(created_at__range=(s_date, e_date + datetime.timedelta(days=1)))
    else: 
        start = now - datetime.timedelta(days=30)
        orders = valid_orders.filter(created_at__gte=start)

    metrics = orders.aggregate(
        total_orders=Count('id', distinct=True),
        total_coupon=Sum('discount_amount'),
        net_revenue=Sum('total_amount'),
        total_sales=Sum('subtotal'),
    )

    total_orders = metrics['total_orders'] or 0
    total_coupon = metrics['total_coupon'] or Decimal('0.00')
    net_revenue = metrics['net_revenue'] or Decimal('0.00')
    total_sales = metrics['total_sales'] or Decimal('0.00')
    # Use simple deduction of subtotal to net_revenue if we need to show total_discount without item-level details
    # Though tax might be included in total, we can approximate discount for dashboard UI keeping it revenue focused
    total_discount = max(total_sales - net_revenue - total_coupon, Decimal('0.00'))

    chart_orders = valid_orders

    if chart_filter == 'yearly':
        trunc_func = TruncYear('created_at')
        chart_orders = chart_orders.filter(created_at__gte=now.replace(year=now.year - 5))
    elif chart_filter == 'daily':
        trunc_func = TruncDate('created_at')
        chart_orders = chart_orders.filter(created_at__gte=now - datetime.timedelta(days=30))
    else:
        chart_filter = 'monthly'
        trunc_func = TruncMonth('created_at')
        chart_orders = chart_orders.filter(created_at__gte=now - datetime.timedelta(days=365))

    graph_data = chart_orders.annotate(date=trunc_func).values('date').annotate(
        sales=Sum('total_amount')
    ).order_by('date')

    # Fill in missing dates for smooth chart rendering
    labels = []
    data = []
    if chart_filter == 'yearly':
        sales_dict = {item['date'].strftime('%Y'): float(item['sales']) for item in graph_data if item['date']}
        start_year = now.year - 5
        for y in range(start_year, now.year + 1):
            lbl = str(y)
            labels.append(lbl)
            data.append(sales_dict.get(lbl, 0.0))
    elif chart_filter == 'daily':
        sales_dict = {item['date'].strftime('%d %b'): float(item['sales']) for item in graph_data if item['date']}
        start_date_chart = (now - datetime.timedelta(days=30)).date()
        for i in range(31):
            d = start_date_chart + datetime.timedelta(days=i)
            lbl = d.strftime('%d %b')
            labels.append(lbl)
            data.append(sales_dict.get(lbl, 0.0))
    else:
        sales_dict = {item['date'].strftime('%b %Y'): float(item['sales']) for item in graph_data if item['date']}
        for i in range(11, -1, -1):
            m = now.month - i
            y = now.year
            while m <= 0:
                m += 12
                y -= 1
            lbl = datetime.date(y, m, 1).strftime('%b %Y')
            labels.append(lbl)
            data.append(sales_dict.get(lbl, 0.0))

    valid_revenue_items = OrderItem.objects.filter(
        order__in=valid_orders
    ).exclude(
        item_status__in=['CANCELLED', 'RETURN_REFUNDED']
    ).filter(
        variant__product__isnull=False
    )

    # Three-level price waterfall — guarantees revenue is never ₹0.00:
    #   1. final_price  → actual purchase price after discount (ideal)
    #   2. original_price → pre-discount price stored at order time
    #   3. variant__price → live variant price (last resort for orders
    #      placed when a bug saved both stored prices as 0)
    safe_unit_price = Case(
        When(final_price__gt=0, then=F('final_price')),
        When(original_price__gt=0, then=F('original_price')),
        default=F('variant__price'),
        output_field=DecimalField(max_digits=10, decimal_places=2)
    )

    # Group by product ID + name so same-named products are never merged
    top_products = valid_revenue_items.values(
        'variant__product__id',
        'variant__product__product_name',
    ).annotate(
        qty_sold=Sum('quantity'),
        revenue=Sum(safe_unit_price * F('quantity'))
    ).order_by('-qty_sold')[:10]

    top_categories = valid_revenue_items.values(
        'variant__product__category__category_name'
    ).annotate(
        qty_sold=Sum('quantity'),
        revenue=Sum(safe_unit_price * F('quantity'))
    ).order_by('-revenue')[:10]

    context = {
        'total_orders': total_orders,
        'total_coupon': total_coupon,
        'net_revenue': net_revenue,
        'total_sales': total_sales,
        'total_discount': total_discount,
        'labels': labels,
        'data': data,
        'filter_type': filter_type,
        'chart_filter': chart_filter,
        'start_date': start_date,
        'end_date': end_date,
        'top_products': top_products,
        'top_categories': top_categories,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax'):
        return JsonResponse(context)

    return render(request, "admin-dashboard.html", context)


@never_cache
def admin_forgot_password(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email, is_superuser=True)
            request.session["admin_email"] = email
            otp = random.randint(100000, 999999)
            admin_hashed_otp = make_password(str(otp))
            request.session["admin_otp"] = admin_hashed_otp
            request.session["admin_otp_created_at"] = time.time()

            send_mail(
                "Email verification OTP",
                f"Your OTP to sign up is {otp}",
                "waseemfaris@gmail.com",
                [email],
                fail_silently=False,
            )

            messages.success(request, "OTP send to mail")
            return redirect("admin-otp-verification")

        except User.DoesNotExist:
            messages.error(request, "Email doesnt found")
            return redirect("admin-forgot-password")
        except:
            messages.error(request, "Something went to wrong")
            return redirect("admin-forgot-password")

    response = render(request, "account/admin-forgot-pass.html")
    return no_cache(response)


@never_cache
def admin_otp_verification(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    created_at = request.session.get("admin_otp_created_at", 0)

    if not created_at:
        messages.error(request, "Session Expired")
        return redirect("admin-forgot-password")

    remaining_time = 60 - (time.time() - created_at)

    if remaining_time < 0:
        remaining_time = 0

    if request.method == "POST":

        otp_attempt = request.session.get("admin_otp_attempt") or 0

        if otp_attempt >= 3:
            request.session.pop("admin_otp", 0)
            request.session.pop("admin_otp_attempt", 0)
            request.session.pop("admin_otp_created_at", 0)
            messages.error(request, "Too Many Attempts")
            return redirect("admin-forgot-password")

        admin_otp = request.POST.get("otp_code")
        otp = request.session.get("admin_otp")

        if not otp:
            messages.error(request, "Session Expired")
            return redirect("admin-forgot-password")

        if remaining_time <= 0:
            request.session.pop("admin_otp", 0)
            request.session.pop("admin_otp_created_at", 0)
            request.session.pop("admin_otp_attempt", 0)
            messages.error(request, "OTP expired resend to get new one")
            return redirect("admin-otp-verification")

        if not admin_otp:
            messages.error(request, "Please fill otp to countinue")
            return redirect("admin-otp-verification")

        if check_password(admin_otp, otp):
            request.session["admin_otp_verified"] = True
            request.session.pop("admin_otp", 0)
            request.session.pop("admin_otp_created_at", 0)
            request.session.pop("admin_resend_otp_attempt", 0)
            messages.success(request, "otp verify successfuly")
            request.session.pop("admin_otp_attempt", 0)
            return redirect("admin-reset-password")
        else:
            otp_attempt += 1
            request.session["admin_otp_attempt"] = otp_attempt
            messages.error(request, "invalid OTP")
            return redirect("admin-otp-verification")

    response = render(
        request,
        "account/admin-otp-verification.html",
        {"remaining_time": remaining_time},
    )
    return no_cache(response)


@never_cache
def admin_reset_password(request):
    is_verified = request.session.get("admin_otp_verified")
    email = request.session.get("admin_email", None)

    if not request.session.get("admin_otp_verified"):
        return redirect("admin-forgot-password")

    if not is_verified or not email:
        messages.error(request, "Session expired. Please try again")
        return redirect("admin-forgot-password")

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not new_password or not confirm_password:
            messages.error(request, "Fill the form to continue")
            return redirect("admin-reset-password")

        if not re.match(password_pattern, new_password):
            messages.error(request, "Password Is Too Week")
            return redirect("admin-reset-password")

        if new_password != confirm_password:
            messages.error(request, "Password doesnt match")
            return redirect("admin-reset-password")

        try:
            user = User.objects.get(email=email)
            if check_password(new_password, user.password):
                messages.error(
                    request, "New password must be different from old password."
                )
                return redirect("admin-reset-password")

            user.set_password(new_password)
            user.save()
            request.session.flush()
            # sometimes flush didnt work so for safety
            request.session.pop("admin_otp_verified", None)
            messages.success(request, "Password changed successfully")
            return redirect("admin-login")
        except User.DoesNotExist:
            messages.error(request, "User not found")
            return redirect("admin-forgot-password")
        except:
            messages.error(request, "Somethink went wrong")
            return redirect("admin-reset-password")

    response = render(request, "account/admin-reset-pass.html")
    return no_cache(response)


def admin_resend_otp(request):
    if request.method == "POST":

        request.session.pop("admin_otp_attempt", 0)
        request.session.pop("admin_otp", 0)
        request.session.pop("admin_otp_created_at", 0)
        resend_otp_attempt = request.session.get("resend_otp_attempt", 0)
        email = request.session.get("admin_email", None)

        if not email:
            messages.error(request, "Session expired. Please try again")
            return redirect("admin-forgot-password")

        if resend_otp_attempt >= 3:
            request.session.pop("admin_otp", 0)
            request.session.pop("admin_resend_otp_attempt", 0)
            request.session.pop("admin_otp_created_at", 0)
            messages.error(request, "Too Many Attempts")
            return redirect("admin-forgot-password")

        otp = random.randint(100000, 999999)
        admin_hashed_otp = make_password(str(otp))
        request.session["admin_otp"] = admin_hashed_otp
        request.session["admin_otp_created_at"] = time.time()

        resend_otp_attempt += 1
        request.session["resend_otp_attempt"] = resend_otp_attempt

        send_mail(
            "Email verification OTP",
            f"Your OTP to sign up is {otp}",
            "waseemfaris@gmail.com",
            [email],
            fail_silently=False,
        )
        messages.success(request, "OTP resent successfully")
        return redirect("admin-otp-verification")


def admin_cancel_reset_password(request):
    request.session.pop("admin_otp", 0)
    request.session.pop("admin_otp_created_at", 0)
    request.session.pop("admin_email", None)
    messages.error(request, "Reset Password Failed")
    return redirect("admin-login")


def admin_logout(request):
    logout(request)
    messages.success(request, "admin logouted succesfully")
    return redirect("admin-login")


@admin_required
def admin_user_management(request):
    page = request.GET.get("page", 1)
    users = User.objects.exclude(is_superuser=True)
    query = request.GET.get("q", "")

    if not request.user.is_authenticated:
        return redirect("admin-login")

    if not request.user.is_superuser:
        return redirect("home")

    if query:
        users = users.filter(Q(username__icontains=query))

    users = users.order_by("-created_at")

    paginator = Paginator(users, 4)
    page_obj = paginator.get_page(page)

    users_count = User.objects.exclude(is_superuser=True).count()
    if request.headers.get("HX-Request"):
        return render(request, "user_table_rows.html", {"page_obj": page_obj})

    return render(
        request,
        "admin-user-management.html",
        {"users_count": users_count, "page_obj": page_obj},
    )


def admin_user_active_toggle(request, id):

    if request.method == "POST":
        try:
            user = User.objects.get(id=id)
            if user.is_blocked == True:
                user.is_blocked = False
                user.save()
                messages.success(request, "user update succesfully")
                return redirect("admin-user-management")
            else:
                user.is_blocked = True
                user.save()
                messages.success(request, "user update succesfully")
                return redirect("admin-user-management")
        except User.DoesNotExist:
            messages.error(request, "user not found")
            return redirect("admin-user-management")


@admin_required
@never_cache
def admin_sales_report(request):
    from core.models import Order, OrderItem
    from django.db.models.functions import TruncDate, TruncMonth
    from decimal import Decimal

    # 1. Date Filtering
    today = timezone.now().date()
    period = request.GET.get('period', 'custom')
    
    if period == 'daily':
        start_date = today
        end_date = today
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
        end_date = today
    elif period == 'yearly':
        start_date = today.replace(month=1, day=1)
        end_date = today
    else:
        # Custom or Default
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        default_start = today - timedelta(days=30)
        
        if start_date_str and end_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                if start_date > end_date:
                    start_date, end_date = end_date, start_date
            except ValueError:
                start_date = default_start
                end_date = today
        else:
            start_date = default_start
            end_date = today

    # 2. Base Query for Valid Orders
    valid_orders = Order.objects.filter(
        Q(payment_status='PAID') | 
        Q(payment_method='COD', items__item_status='DELIVERED')
    ).distinct()

    filtered_orders = valid_orders.filter(created_at__date__range=[start_date, end_date])

    # 2.1 Additional Search and Status Filters
    query = request.GET.get('q', '')
    if query:
        filtered_orders = filtered_orders.filter(
            Q(order_number__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__email__icontains=query)
        )
    
    status_filter = request.GET.get('status', 'All Status')
    if status_filter and status_filter != 'All Status':
        filtered_orders = filtered_orders.filter(payment_status=status_filter.upper())

    # 3. Aggregations (Top Metric Cards)
    metrics = filtered_orders.aggregate(
        total_revenue=Sum('total_amount'),
        total_orders=Count('id', distinct=True),
        coupon_deduction=Sum('discount_amount')
    )
    
    # Offer discounts from OrderItem
    total_offer_discounts = OrderItem.objects.filter(
        order__in=filtered_orders
    ).exclude(item_status__in=['CANCELLED', 'RETURN_REFUNDED']).aggregate(
        total=Sum(F('discount_amount') * F('quantity'))
    )['total'] or Decimal('0.00')

    products_sold = OrderItem.objects.filter(
        order__in=filtered_orders
    ).exclude(item_status__in=['CANCELLED', 'RETURN_REFUNDED']).aggregate(
        total_qty=Sum('quantity')
    )['total_qty'] or 0

    total_revenue = metrics['total_revenue'] or Decimal('0.00')
    total_orders_count = metrics['total_orders'] or 0
    coupon_deduction = metrics['coupon_deduction'] or Decimal('0.00')

    # 4. Chart Data: Revenue Overview (Daily)
    daily_revenue = filtered_orders.annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        revenue=Sum('total_amount')
    ).order_by('date')

    # Prepare labels and data for JS
    daily_labels = []
    daily_values = []
    curr = start_date
    revenue_dict = {item['date']: float(item['revenue']) for item in daily_revenue}
    
    while curr <= end_date:
        daily_labels.append(curr.strftime('%d %b'))
        daily_values.append(revenue_dict.get(curr, 0.0))
        curr += timedelta(days=1)

    # 5. Chart Data: Monthly Growth (Last 12 Months)
    # Ensure we show all last 12 months even if revenue is 0
    monthly_data = []
    for i in range(11, -1, -1):
        # Calculate start of month i months ago
        first_day = (today.replace(day=1) - timedelta(days=i*31)).replace(day=1)
        # Calculate end of that month
        if first_day.month == 12:
            next_month = first_day.replace(year=first_day.year + 1, month=1)
        else:
            next_month = first_day.replace(month=first_day.month + 1)
        
        month_revenue = valid_orders.filter(
            created_at__date__gte=first_day,
            created_at__date__lt=next_month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        monthly_data.append({
            'label': first_day.strftime('%b'),
            'value': float(month_revenue)
        })

    monthly_labels = [m['label'] for m in monthly_data]
    monthly_values = [m['value'] for m in monthly_data]

    # 6. Recent Transactions Table (Paginated - Limit 5)
    transactions_list = filtered_orders.order_by('-created_at').select_related('user')
    paginator = Paginator(transactions_list, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 7. Export Functionality
    if request.GET.get('export') == 'csv':
        # Generate clean filename
        filename = f"sales_report_{start_date.strftime('%Y_%m_%d')}_to_{end_date.strftime('%Y_%m_%d')}.csv"
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Add UTF-8 BOM for Excel to recognize UTF-8 encoding immediately
        response.write('\ufeff'.encode('utf8'))
        
        writer = csv.writer(response)
        # Professional Headers
        writer.writerow(['Order ID', 'Date', 'Customer Name', 'Status', 'Payment Method', 'Total Amount', 'Discount Applied', 'Final Amount'])
        
        if not transactions_list.exists():
            writer.writerow(['No data available'] + ['-'] * 7)
        else:
            for order in transactions_list:
                writer.writerow([
                    order.order_number,
                    order.created_at.strftime('%Y-%m-%d'),
                    order.user.username,
                    order.payment_status,
                    order.payment_method,
                    "{:.2f}".format(order.subtotal),
                    "{:.2f}".format(order.discount_amount),
                    "{:.2f}".format(order.total_amount)
                ])
        return response

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders_count,
        'products_sold': products_sold,
        'total_offer_discounts': total_offer_discounts,
        'coupon_deduction': coupon_deduction,
        'daily_labels': daily_labels,
        'daily_values': daily_values,
        'monthly_labels': monthly_labels,
        'monthly_values': monthly_values,
        'page_obj': page_obj,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'query': query,
        'status_filter': status_filter,
        'period': period,
        # Growth placeholders (as requested)
        'rev_growth': 24.8, 
        'ord_growth': 15.2,
        'prod_growth': 12.5,
    }
    
    return render(request, "admin-sales-report.html", context)
