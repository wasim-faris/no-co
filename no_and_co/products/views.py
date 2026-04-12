from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Variant, VariantImage, Size
from category.models import Category, Subcategory
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Min, Sum, Prefetch, Q
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from admin_dashboard.decorators import admin_required
from django.views.decorators.cache import never_cache


@admin_required
@never_cache
def admin_products(request):
    status = request.GET.get("status")
    if status == "archived":
        product = Product.objects.filter(is_deleted=True)
    else:
        product = Product.objects.filter(is_deleted=False)

    query = request.GET.get("q")
    if query:
        product = product.filter(
            Q(product_name__icontains=query)
            | Q(category__category_name__icontains=query)
            | Q(subcategory__subcategory_name__icontains=query)
        )

    if request.method == "POST":
        restore_id = request.POST.get("restore_id")
        if restore_id:
            restore_product = get_object_or_404(Product, id=restore_id)
            restore_product.is_deleted = False
            restore_product.save()
            messages.success(request, "Product restored")
            return redirect("admin-products")

        delete_id = request.POST.get("delete_id")
        if delete_id:
            delete_product = get_object_or_404(Product, id=delete_id)
            delete_product.delete()
            messages.success(request, "Product deleted permanently")
            return redirect("admin-products")

    all_products = Product.objects.filter(is_deleted=False)

    product = product.prefetch_related(
        Prefetch(
            "variants",
            queryset=Variant.objects.filter(is_default=True, is_deleted=False),
            to_attr="default_variants",
        )
    ).order_by("-id")

    count = all_products.count()
    active_count = all_products.filter(is_active=True).count()
    inactive_count = all_products.filter(is_active=False).count()

    paginator = Paginator(product, 4)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "product/admin-products.html",
        {
            "page_obj": page_obj,
            "count": count,
            "active_count": active_count,
            "inactive_count": inactive_count,
        },
    )


def get_subcategories(request, category_id):
    subs = Subcategory.objects.filter(
        category_id=category_id, is_active=True, is_deleted=False
    )
    return JsonResponse({"subcategories": list(subs.values("id", "subcategory_name"))})


@admin_required
@never_cache
def admin_product_details(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_variant":
            size_name = request.POST.get("size")
            size_obj, _ = Size.objects.get_or_create(name=size_name)

            try:
                stock_val = int(request.POST.get("stock", 0))
                if stock_val < 0 or stock_val > 100000:
                    messages.error(request, "Stock must be between 0 and 100,000")
                    return redirect("admin-product-details", id=product.id)
            except ValueError:
                messages.error(request, "Invalid stock value")
                return redirect("admin-product-details", id=product.id)
            if Variant.objects.filter(
                product=product,
                size_id=size_obj.id,
                color=request.POST.get("color"),
                is_deleted=False,
            ).exists():
                messages.warning(
                    request, "A variant with this size and color already exists."
                )
                return redirect("admin-product-details", id=product.id)

            Variant.objects.create(
                product=product,
                size=size_obj,
                color=request.POST.get("color"),
                color_hex=request.POST.get("color_hex"),
                price=request.POST.get("price"),
                stock=stock_val,
                is_active=request.POST.get("is_active") == "true",
                is_default=request.POST.get("is_default") == "true",
            )
            messages.success(request, "Product variant created successfully")
            return redirect("admin-product-details", id=product.id)

        if action == "edit_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            size = request.POST.get("size")
            price = request.POST.get("price")

            try:
                stock_val = int(request.POST.get("stock", 0))
                if stock_val < 0 or stock_val > 100000:
                    messages.error(request, "Stock must be between 0 and 100,000")
                    return redirect("admin-product-details", id=product.id)
            except ValueError:
                messages.error(request, "Invalid stock value")
                return redirect("admin-product-details", id=product.id)

            color = request.POST.get("color")
            is_active = request.POST.get("is_active") == "true"
            is_default = request.POST.get("is_default") == "true"

            if is_default:
                Variant.objects.filter(is_default=True, product=variant.product).update(
                    is_default=False
                )

            size_obj, _ = Size.objects.get_or_create(name=size)
            variant.size = size_obj
            variant.price = price
            variant.stock = stock_val
            variant.color = color
            variant.color_hex = request.POST.get("color_hex")
            variant.is_active = is_active
            variant.is_default = is_default
            variant.save()
            messages.success(request, "Product edited succesfully")
            return redirect("admin-product-details", id=product.id)

        if action == "delete_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.is_deleted = True
            variant.save()
            messages.success(request, "Product variant deleted succesfully")
            return redirect("admin-product-details", id=product.id)

        if action == "set_default":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.is_default = True
            variant.save()
            messages.success(request, "Default variant updated")
            return redirect("admin-product-details", id=product.id)

        deleted_product = request.POST.get("deleted_product")
        if deleted_product:
            product.is_deleted = True
            product.save()
            messages.success(request, "Product moved to archives")
            return redirect("admin-products")

        if action == "toggle_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            if not variant.is_default:
                variant.is_active = not variant.is_active
                variant.save()
                messages.success(request, "Status updated")
            else:
                messages.warning(request, "Default variant must stay active")

        return redirect("admin-product-details", id=product.id)

    category = Category.objects.filter(is_deleted=False, is_active=True)
    subcategory = Subcategory.objects.filter(is_deleted=False, is_active=True)

    return render(
        request,
        "product/admin-product-details.html",
        {
            "product": product,
            "category": category,
            "subcategory": subcategory,
        },
    )


@admin_required
@never_cache
def admin_product_management(request, id=None):
    if id:
        product = get_object_or_404(Product, id=id)
    else:
        product = None

    if request.method == "POST":
        deleted_product = request.POST.get("deleted_product")
        if deleted_product:
            product_to_delete = get_object_or_404(Product, id=deleted_product)
            product_to_delete.is_deleted = True
            product_to_delete.save()
            messages.success(request, "Product moved to archives")
            return redirect("admin-products")

        product_name = request.POST.get("name")
        description_fit = request.POST.get("description")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")
        delivery_returns = request.POST.get("delivery_returns")
        materials = request.POST.get("fabric")
        washing = request.POST.get("washing")

        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)

        if product:
            product.product_name = product_name
            product.description_fit = description_fit
            product.materials = materials
            product.care_guide = washing
            product.delivery_returns = delivery_returns
            product.category = category
            product.subcategory = subcategory
            product.save()
            messages.success(request, "Product Updated")
        else:
            product = Product.objects.create(
                product_name=product_name,
                description_fit=description_fit,
                materials=materials,
                care_guide=washing,
                delivery_returns=delivery_returns,
                category=category,
                subcategory=subcategory,
            )
            messages.success(request, "Product Created")

        return redirect("admin-products")

    category_option = Category.objects.filter(is_deleted=False, is_active=True)
    return render(
        request,
        "product/product-form.html",
        {"product": product, "category_option": category_option},
    )


def admin_soft_delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.is_deleted = True
    product.save()
    messages.success(request, "Product deleted")
    return redirect("admin-products")


def admin_product_toggle(request, id):
    product = get_object_or_404(Product, id=id)
    product.is_active = not product.is_active
    product.save()
    messages.success(
        request, f"Product {'active' if product.is_active else 'inactive'} successfully"
    )
    return redirect(request.META.get("HTTP_REFERER"))


@admin_required
@never_cache
def admin_variants(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_variant":
            sizes = request.POST.getlist("sizes")
            color = request.POST.get("color")
            color_hex = request.POST.get("color_hex")
            price = request.POST.get("price")

            try:
                stock_val = int(request.POST.get("stock", 0))
                if stock_val < 0 or stock_val > 100000:
                    messages.error(request, "Stock must be between 0 and 100,000")
                    return redirect("admin-variants", id=product.id)
            except ValueError:
                messages.error(request, "Invalid stock value")
                return redirect("admin-variants", id=product.id)

            is_active = request.POST.get("is_active") == "true"

            if not sizes:
                messages.error(request, "Select at least one size")
                return redirect("admin-variants", id=product.id)

            added_count = 0
            skipped_count = 0

            for size_id in sizes:
                exists = Variant.objects.filter(
                    product=product, size_id=size_id, color=color, is_deleted=False
                ).exists()
                if not exists:
                    variant = Variant.objects.create(
                        product=product,
                        size_id=size_id,
                        color=color,
                        price=price,
                        stock=stock_val,
                        color_hex=color_hex,
                        is_active=is_active,
                    )

                    primary_val = request.POST.get("primary_image", "new_0")

                    for i in range(4):
                        img = request.FILES.get(f"image_{i}")
                        if img:
                            img.seek(0)
                            is_primary = f"new_{i}" == primary_val
                            VariantImage.objects.create(
                                variant=variant, image=img, is_primary=is_primary
                            )

                    if (
                        variant.images.exists()
                        and not variant.images.filter(is_primary=True).exists()
                    ):
                        first_img = variant.images.first()
                        first_img.is_primary = True
                        first_img.save()

                    added_count += 1
                else:
                    skipped_count += 1

            if added_count > 0:
                msg = f"Successfully added {added_count} variant(s)."
                if skipped_count > 0:
                    msg += f" ({skipped_count} already existed and were skipped)"
                messages.success(request, msg)
                return redirect(request.path_info)
            else:
                messages.warning(
                    request,
                    "No variants were added (all selected combinations already exist).",
                )

            return redirect(request.path_info + "?" + request.GET.urlencode())

        elif action == "edit_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            sizes = request.POST.getlist("sizes")

            try:
                stock_val = int(request.POST.get("stock", 0))
                if stock_val < 0 or stock_val > 100000:
                    messages.error(request, "Stock must be between 0 and 100,000")
                    return redirect("admin-variants", id=product.id)
                variant.stock = stock_val
            except ValueError:
                messages.error(request, "Invalid stock value")
                return redirect("admin-variants", id=product.id)

            variant.price = float(request.POST.get("price", 0))
            if sizes and sizes[0]:
                variant.size_id = int(sizes[0])

            variant.color = request.POST.get("color")
            variant.color_hex = request.POST.get("color_hex")
            variant.is_active = "true" in request.POST.getlist("is_active")
            variant.is_default = "true" in request.POST.getlist("is_default")

            for key in request.POST:
                if key.startswith("delete_image_") and request.POST.get(key) == "true":
                    img_id = key.split("_")[-1]
                    VariantImage.objects.filter(id=img_id, variant=variant).delete()

            primary_val = request.POST.get("primary_image", "")
            for i in range(4):
                img = request.FILES.get(f"image_{i}")
                if img:
                    is_primary = f"new_{i}" == primary_val
                    VariantImage.objects.create(
                        variant=variant, image=img, is_primary=is_primary
                    )

            if primary_val.startswith("existing_") and primary_val != "":
                img_id = primary_val.split("_")[-1]
                variant.images.exclude(id=img_id).update(is_primary=False)
                variant.images.filter(id=img_id).update(is_primary=True)
            elif primary_val.startswith("new_"):
                new_primary = variant.images.filter(is_primary=True).last()
                if new_primary:
                    variant.images.exclude(id=new_primary.id).update(is_primary=False)

            if (
                variant.images.exists()
                and not variant.images.filter(is_primary=True).exists()
            ):
                first = variant.images.first()
                first.is_primary = True
                first.save()

            with transaction.atomic():
                variant.save()

            messages.success(request, "Variant updated successfully")
            return redirect(request.path_info + "?" + request.GET.urlencode())

        elif action == "toggle_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            if variant.is_default:
                messages.warning(request, "Default variant must stay active")
            else:
                variant.is_active = not variant.is_active
                variant.save()
                messages.success(
                    request,
                    f"Variant {'active' if variant.is_active else 'inactive'} successfully",
                )

        elif action == "set_default":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.is_default = True
            variant.save()
            messages.success(request, "Default variant updated")

        elif action == "delete_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.is_deleted = True
            variant.save()
            messages.success(request, "Variant archived successfully")

        elif action == "restore_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.is_deleted = False
            variant.is_active = False
            variant.save()
            messages.success(request, "Variant restored as inactive")

        elif action == "permanent_delete_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.delete()
            messages.success(request, "Variant deleted permanently")

        return redirect(request.path_info + "?" + request.GET.urlencode())

    variants = (
        Variant.objects.filter(product=product)
        .order_by("-is_default", "-id")
        .prefetch_related("images")
    )

    q = request.GET.get("q")
    if q:
        variants = variants.filter(
            Q(color__icontains=q) | Q(size__name__icontains=q) | Q(sku__icontains=q)
        )

    status = request.GET.get("status")
    if status == "archived":
        variants = variants.filter(is_deleted=True)
    elif status == "low_stock":
        variants = variants.filter(is_deleted=False, stock__lte=5)
    else:
        variants = variants.filter(is_deleted=False)

        if status == "active":
            variants = variants.filter(is_active=True)
        elif status == "inactive":
            variants = variants.filter(is_active=False)

    all_variants = Variant.objects.filter(product=product, is_deleted=False)
    active_count = all_variants.filter(is_active=True).count()
    inactive_count = all_variants.filter(is_active=False).count()
    total_count = all_variants.count()

    paginator = Paginator(variants, 4)
    page_obj = paginator.get_page(request.GET.get("page"))
    sizes = Size.objects.all()
    context = {
        "product": product,
        "variants": page_obj,
        "page_obj": page_obj,
        "active_count": active_count,
        "inactive_count": inactive_count,
        "total_count": total_count,
        "sizes": sizes,
    }

    return render(request, "variant/admin-variants.html", context)
