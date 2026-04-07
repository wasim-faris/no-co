from django.shortcuts import render, redirect
from .models import Category,Subcategory
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from admin_dashboard.decorators import admin_required
from django.views.decorators.cache import never_cache

@admin_required
@never_cache
def admin_category(request):

    page_number = request.GET.get("page")
    query = request.GET.get("q", "")


    if request.method == "POST":
        action = request.POST.get("action")

        if action == "toggle":
            cat = Category.objects.get(id=request.POST.get("category_id"))
            cat.is_active = not cat.is_active
            cat.save()
            messages.success(request, "Updated successfully")
            return redirect("admin-category")

        if action == "create":
            name = request.POST.get("category_name")
            name = name.strip().upper()

            if Category.objects.filter(category_name = name).exists():
                messages.error(request, "Category already exists or archived")
                return redirect("admin-category")

            if not name or len(name.strip()) < 3:
                messages.error(request, "Please enter at least 3 characters")
                return redirect("admin-category")

            Category.objects.create(
                category_name=name,
                is_active=request.POST.get("is_active") == "true"
            )
            messages.success(request, "Category created")
            return redirect("admin-category")

        if action == "delete":
            cat = Category.objects.get(id=request.POST.get("category_id"))
            cat.is_deleted = True
            cat.save()
            messages.success(request, "Deleted successfully")
            return redirect("admin-category")

        if action == "edit":
            cat = Category.objects.get(id=request.POST.get("category_id"))
            cat.category_name = request.POST.get("category_name")
            cat.updated_at = timezone.now()
            cat.save()
            messages.success(request, "Category edited")
            return redirect("admin-category")

        if action == "restore":
            cat = Category.objects.get(id=request.POST.get("category_id"))
            cat.is_deleted = False
            cat.save()
            messages.success(request, "Restored Successfully")
            return redirect("admin-category")

        if action == "permanent_delete_category":
            cat = get_object_or_404(Category, id=request.POST.get("category_id")).delete()
            messages.success(request, "Category permanently deleted")
            return redirect("admin-category")


    # Base Queryset
    status_filter = request.GET.get("status", "live")
    if status_filter == "archived":
        category_list = Category.objects.filter(is_deleted=True)
    else:
        category_list = Category.objects.filter(is_deleted=False)

    # Search Logic
    query = request.GET.get("q")
    if query:
        category_list = category_list.filter(Q(category_name__icontains=query))

    category_list = category_list.order_by("-id")

    # Pagination
    paginator = Paginator(category_list, 4)
    page_obj = paginator.get_page(page_number)

    # Statistics (Total counts for the current status filter, or overall)
    all_categories = Category.objects.filter(is_deleted=False)
    count = all_categories.count()
    active_count = all_categories.filter(is_active=True).count()
    inactive_count = all_categories.filter(is_active=False).count()
    subcategory_count = Subcategory.objects.filter(is_deleted=False).count()

    return render(
        request,
        "admin-category.html",
        {
            "page_obj": page_obj,
            "count": count,
            "active_count": active_count,
            "inactive_count": inactive_count,
            "search_query":query,
            "subcategory_count":subcategory_count
        },
    )

@admin_required
@never_cache
def admin_subcategory(request):
    page_number = request.GET.get("page")
    query = request.GET.get("q", "")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "toggle":
            sub = get_object_or_404(Subcategory, id=request.POST.get("subcategory_id"))
            sub.is_active = not sub.is_active
            sub.save()
            messages.success(request, "Updated successfully")
            return redirect("admin-subcategory")

        if action == "create":
            parent_category = request.POST.get("parent_category")
            name = request.POST.get("subcategory_name")

            name = name.strip().upper()

            if Subcategory.objects.filter(subcategory_name = name, category = parent_category).exists():
                messages.error(request, "Subcategory already exists or archived")
                return redirect("admin-subcategory")

            if not name or len(name.strip()) < 3:
                messages.error(request, "Please enter at least 3 characters")
                return redirect("admin-subcategory")

            category = Category.objects.get(id=parent_category)

            if not category.is_active:
                messages.error(request, "Category currently not found")
                return redirect("admin-subcategory")

            Subcategory.objects.create(
                subcategory_name=name,
                category = category,
                is_active=request.POST.get("is_active") == "true"
            )
            messages.success(request, "Subcategory created")
            return redirect("admin-subcategory")

        if action == "delete":
            sub = get_object_or_404(Subcategory, id=request.POST.get("subcategory_id"))
            sub.is_deleted = True
            sub.save()
            messages.success(request, "Deleted successfully")
            return redirect("admin-subcategory")

        if action == "edit":
            name = request.POST.get("subcategory_name")

            if len(name)<3:
                messages.error(request, "Please make sure word more than 3 words")
                return redirect("admin-subcategory")

            if not name:
                messages.error(request,"Please fill form")
                return redirect("admin-subcategory")

            sub = get_object_or_404(Subcategory, id=request.POST.get("subcategory_id"))
            sub.subcategory_name = request.POST.get("subcategory_name")

            if not sub.subcategory_name:
                messages.error(request, "Please fill the filed")
                return redirect("admin-subcategory")

            sub.category_id = request.POST.get("parent_category")
            sub.updated_at = timezone.now()
            sub.save()
            messages.success(request, "Category edited")
            return redirect("admin-subcategory")

        if action == "restore":
            sub = get_object_or_404(Subcategory, id=request.POST.get("subcategory_id"))
            sub.is_deleted = False
            sub.save()
            messages.success(request, "Restored Successfully")
            return redirect("admin-subcategory")

        if action == "permanent_delete":
            sub = get_object_or_404(Subcategory, id=request.POST.get("subcategory_id"))
            sub.delete()
            messages.error(request, "Permaently deleted")
            return redirect("admin-subcategory")

    status_filter = request.GET.get("status", "live")

    if status_filter == "archived":
        subcategory = Subcategory.objects.filter(is_deleted=True).order_by("-id")
    else:
        subcategory= Subcategory.objects.filter(is_deleted=False , category__is_deleted = False , category__is_active=True).order_by("-id")

    if query:
        from django.db.models import Q
        subcategory = subcategory.filter(
            Q(subcategory_name__icontains=query) |
            Q(category__category_name__icontains=query)
        )

    subcategory = subcategory.order_by("-id")

    category = Category.objects.filter(is_deleted=False).order_by("-id")
    paginator = Paginator(subcategory, 4)
    page_obj = paginator.get_page(page_number)


    live_subcategory = Subcategory.objects.filter(is_deleted=False, category__is_deleted = False ,category__is_active = True).order_by("-id")

    subcategory_count = live_subcategory.count()
    active_subcategory = live_subcategory.filter(is_active=True).count()
    inactive_subcategory = live_subcategory.filter(is_active=False).count()

    return render(request, "admin-subcategory.html",{
        "query": query,
        "category":category,
        "page_obj":page_obj,
        "subcategory_count": subcategory_count,
        "active_subcategory": active_subcategory,
        "inactive_subcategory": inactive_subcategory
    })
