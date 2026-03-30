from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Variant, ProductImage,VariantImage
from category.models import Category, Subcategory
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Min, Sum, Prefetch, Q
from django.core.paginator import Paginator

def admin_products(request):
    status = request.GET.get("status")
    if status == "archived":
        product = Product.objects.filter(is_deleted=True)
    else:
        product = Product.objects.filter(is_deleted=False)

    product = product.annotate(
        min_price=Min("variants__price"),
        total_stock=Sum("variants__stock")
    ).prefetch_related(
        Prefetch("productimage_set", queryset=ProductImage.objects.filter(is_primary=True), to_attr="primary_img")
    )

    query = request.GET.get("q")
    if query:
        product = product.filter(
            Q(product_name__icontains=query) |
            Q(category__category_name__icontains=query) |
            Q(subcategory__subcategory_name__icontains=query)
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
    all_products = all_products.order_by("-id")
    count = all_products.count()
    active_count = all_products.filter(is_active=True).count()
    inactive_count = all_products.filter(is_active=False).count()

    paginator = Paginator(product, 4)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "product/admin-products.html", {
        "page_obj": page_obj,
        "count": count,
        "active_count": active_count,
        "inactive_count": inactive_count
    })

def get_subcategories(request, category_id):
    subs = Subcategory.objects.filter(category_id=category_id, is_active=True, is_deleted=False)
    return JsonResponse({"subcategories": list(subs.values("id", "subcategory_name"))})

def admin_product_details(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_variant":
            Variant.objects.create(
                product = product,
                size = request.POST.get("size"),
                color = request.POST.get("color"),
                price = request.POST.get("price"),
                stock = request.POST.get("stock"),
                is_active = request.POST.get("is_active") == "true",
                is_default = request.POST.get("is_default") == "true",
            )
            messages.success(request, "Product variant created")
            return redirect("admin-product-details", id=product.id)

        if action == "edit_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant , id=variant_id)

            variant.size = request.POST.get("size")
            variant.price = request.POST.get("price")
            variant.stock = request.POST.get("stock")
            variant.color = request.POST.get("color")
            variant.is_active = request.POST.get("is_active")=="true"
            variant.is_default = request.POST.get("is_default") == "true"

            variant.save()
            messages.error(request, "Product edited succesfully")
            return redirect("admin-product-details", id=product.id)

        if action == "delete_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            variant.delete()
            messages.success(request,"Product variant deleted succesfully")
            return redirect("admin-product-details", id=product.id)

        deleted_product = request.POST.get("deleted_product")
        if deleted_product:
            product.is_deleted = True
            product.save()
            messages.success(request, "Product moved to archives")
            return redirect("admin-products")


    category = Category.objects.filter(is_deleted=False, is_active=True)
    subcategory = Subcategory.objects.filter(is_deleted=False, is_active=True)

    # Simple READ-ONLY details view as requested
    return render(request, "product/admin-product-details.html", {
        "product": product,
        "category": category,
        "subcategory": subcategory,
    })


def admin_product_management(request, id=None):
    if id:
        product = get_object_or_404(Product, id=id)
    else:
        product = None

    if request.method == "POST":
        # 1. Handle Delete Request FIRST
        deleted_product = request.POST.get("deleted_product")
        if deleted_product:
            product_to_delete = get_object_or_404(Product, id=deleted_product)
            product_to_delete.is_deleted = True
            product_to_delete.save()
            messages.success(request, "Product moved to archives")
            return redirect("admin-products")

        # 2. AJAX IMAGE ACTIONS (Delete / Upload)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get("action")
            if action == "upload_image" and product:
                if product.productimage_set.count() >= 4:
                    return JsonResponse({"status": "error", "message": "Maximum 4 images allowed"}, status=400)
                image_file = request.FILES.get("image")
                if image_file:
                    is_primary = not product.productimage_set.filter(is_primary=True).exists()
                    new_img = ProductImage.objects.create(product=product, image=image_file, is_primary=is_primary)
                    return JsonResponse({"status": "success", "url": new_img.image.url, "id": new_img.id, "is_primary": new_img.is_primary})

            if action == "delete_image" and product:
                image_id = request.POST.get("image_id")
                img = ProductImage.objects.filter(id=image_id, product=product).first()
                if img:
                    was_primary = img.is_primary
                    img.delete()
                    if was_primary:
                        next_img = product.productimage_set.first()
                        if next_img:
                            next_img.is_primary = True
                            next_img.save()
                    return JsonResponse({"status": "success", "message": "Image deleted"})
            return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)

        # 3. Standard Form Image Upload (Create flow)
        # Note: Handled after product creation below for new products

        # Standard Form Submit
        product_name = request.POST.get("name")
        description_fit = request.POST.get("description")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")
        delivery_returns = request.POST.get("delivery_returns")
        fabric = request.POST.get("fabric")
        washing = request.POST.get("washing")

        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)

        if product:
            product.product_name = product_name
            product.description_fit = description_fit
            product.materials = fabric
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
                materials=fabric,
                care_guide=washing,
                delivery_returns=delivery_returns,
                category=category,
                subcategory=subcategory
            )
            messages.success(request, "Product Created")

        # Save standard images if provided (Create flow)
        for i in range(1, 5):
            img = request.FILES.get(f"image_{i}")
            if img and product.productimage_set.count() < 4:
                is_primary = not product.productimage_set.filter(is_primary=True).exists()
                ProductImage.objects.create(product=product, image=img, is_primary=is_primary)

        return redirect("admin-products")

    category_option = Category.objects.filter(is_deleted=False, is_active=True)
    return render(request, "product/product-form.html", {
        "product": product,
        "category_option": category_option
    })

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
    messages.success(request, f"Product {'active' if product.is_active else 'inactive'} successfully")
    return redirect("admin-product-details", id=product.id)

def admin_variants(request, id):
    product = get_object_or_404(Product, id=id)
    variants = product.variants.all().order_by('-is_default', '-id')

    if request.method == "POST":
        print(request.POST)

        action = request.POST.get("action")

        if action == "add_variant":
            variant = Variant.objects.create(
            product = product,
            size = request.POST.get("size"),
            color = request.POST.get("color"),
            stock = request.POST.get("stock"),
            price = request.POST.get("price"),
            is_active = request.POST.get("is_active") == "true",
            is_default = request.POST.get("is_default")== "true",

            )

            for i in range(1,5):
                image = request.FILES.get(f'image_{i}')

                if image:
                    VariantImage.objects.create(
                        variant = variant,
                        image=image,
                        is_primary = (i==1)
                    )
            messages.success(request, "Product variant created successfully")
            return redirect("admin-variants", id=product.id)

        if action == "edit_variant":
            size = request.POST.get("size")
            color = request.POST.get("color")
            stock = request.POST.get("stock")
            price = request.POST.get("price")
            is_active = request.POST.get("is_active")== "true"
            is_default = request.POST.get("is_default")=="true"
            variant_id = request.POST.get("variant_id")

            variant = get_object_or_404(Variant, id=variant_id)

            if variant.is_default:
                Variant.objects.filter(product = variant.product.id, is_default = True).exclude(id=variant.id).update(is_default = False)

            variant.size = size
            variant.color = color
            variant.stock = stock
            variant.price = price
            variant.is_active = is_active
            variant.is_default = is_default

            variant.save()

        if action == "delete_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant , id=variant_id)
            variant.delete()
            messages.success(request,"Variant deleted successfully")
            return redirect("admin-variants", id=product.id)

        if action == "toggle_variant":
            variant_id = request.POST.get("variant_id")
            variant = get_object_or_404(Variant, id=variant_id)
            if variant.is_active:
                variant.is_active = False
                variant.save()
                messages.success(request, "Product update succesfully")
                return redirect("admin-variants", id=product.id)
            else:
                variant.is_active = True
                variant.save()
                messages.success(request, "Product update successfully")
                return redirect("admin-variants", id=product.id)

    total_variants = variants.count()
    active_variants = variants.filter(is_active=True).count()

    paginator = Paginator(variants, 4)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "product": product,
        "variants": page_obj,
        "page_obj": page_obj,
        "total_variants": total_variants,
        "active_variants": active_variants,
    }
    return render(request, "variant/admin-variants.html", context)
