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
from django.db.models import Q
from django.core.paginator import Paginator

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
    from django.db.models import Sum, Count, F, Q
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
    
    orders = Order.objects.filter(
        Q(payment_status='PAID') | 
        Q(payment_method='COD', items__item_status='DELIVERED')
    ).distinct()

    if filter_type == 'daily':
        start = now - datetime.timedelta(days=7)
        orders = orders.filter(created_at__gte=start)
    elif filter_type == 'weekly':
        start = now - datetime.timedelta(weeks=12)
        orders = orders.filter(created_at__gte=start)
    elif filter_type == 'yearly':
        start = now.replace(year=now.year - 5)
        orders = orders.filter(created_at__gte=start)
    elif filter_type == 'custom' and start_date and end_date:
        s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        orders = orders.filter(created_at__range=(s_date, e_date + datetime.timedelta(days=1)))
    else: 
        start = now - datetime.timedelta(days=30)
        orders = orders.filter(created_at__gte=start)

    metrics = orders.aggregate(
        total_orders=Count('id', distinct=True),
        total_coupon=Sum('discount_amount'),
        net_revenue=Sum('total_amount'),
    )
    
    order_items = OrderItem.objects.filter(order__in=orders)
    item_metrics = order_items.aggregate(
        total_sales=Sum(F('final_price') * F('quantity')),
        total_discount=Sum((F('original_price') - F('final_price')) * F('quantity'))
    )

    total_orders = metrics['total_orders'] or 0
    total_coupon = metrics['total_coupon'] or Decimal('0.00')
    net_revenue = metrics['net_revenue'] or Decimal('0.00')
    total_sales = item_metrics['total_sales'] or Decimal('0.00')
    total_discount = item_metrics['total_discount'] or Decimal('0.00')

    if download_format == 'excel':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order Number', 'Date', 'Total Sales', 'Coupon Deduction', 'Net Revenue'])
        for order in orders.order_by('-created_at'):
            writer.writerow([order.order_number, order.created_at.strftime('%Y-%m-%d %H:%M'), order.subtotal, order.discount_amount, order.total_amount])
        return response

    if download_format == 'pdf':
        try:
            from xhtml2pdf import pisa
            template = get_template("sales_report_pdf.html")
            context_pdf = {
                'orders': orders.order_by('-created_at'),
                'total_orders': total_orders,
                'total_sales': total_sales,
                'total_discount': total_discount,
                'total_coupon': total_coupon,
                'net_revenue': net_revenue,
                'filter_type': filter_type,
            }
            html_string = template.render(context_pdf)
            buffer = BytesIO()
            pdf_result = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), buffer)
            if not pdf_result.err:
                response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
                return response
        except ImportError:
            pass

    chart_orders = Order.objects.filter(
        Q(payment_status='PAID') | 
        Q(payment_method='COD', items__item_status='DELIVERED')
    ).distinct()

    if chart_filter == 'yearly':
        trunc_func = TruncYear('created_at')
        chart_orders = chart_orders.filter(created_at__gte=now.replace(year=now.year - 5))
    else:
        trunc_func = TruncMonth('created_at')
        chart_orders = chart_orders.filter(created_at__gte=now - datetime.timedelta(days=365))

    graph_data = chart_orders.annotate(date=trunc_func).values('date').annotate(
        sales=Sum('total_amount')
    ).order_by('date')

    labels = [item['date'].strftime('%Y-%m') if chart_filter == 'monthly' else item['date'].strftime('%Y') for item in graph_data] if graph_data else []
    data = [float(item['sales']) for item in graph_data] if graph_data else []

    valid_order_items = OrderItem.objects.filter(
        Q(order__payment_status='PAID') | 
        Q(order__payment_method='COD', item_status='DELIVERED')
    )
    
    top_products = valid_order_items.values('variant__product__product_name').annotate(
        qty_sold=Sum('quantity'),
        revenue=Sum(F('final_price') * F('quantity'))
    ).order_by('-qty_sold')[:10]

    top_categories = valid_order_items.values('variant__product__category__category_name').annotate(
        qty_sold=Sum('quantity'),
        revenue=Sum(F('final_price') * F('quantity'))
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
