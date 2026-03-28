from django.shortcuts import render,redirect
from .models import Product,Variant,ProductImage
from category.models import Category,Subcategory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
import uuid
from django.db.models import Min,Max,Sum,Prefetch
# Create your views here.

def admin_products(request):
    product = Product.objects.all().annotate(
        min_price = Min("variants__price"),
        total_stock = Sum("variants__stock")
    ).prefetch_related(
        Prefetch("productimage_set", queryset = ProductImage.objects.filter(is_primary = True),
        to_attr = "primary_img"
    ))
    return render(request, "product/admin-products.html",{
        "product":product
    })

def add_product(request):
    if request.method == "POST":
        print(request.POST.get("subcategory"))
        product_name = request.POST.get("name")
        description_fit = request.POST.get("description")
        category_id = request.POST.get("category")
        subcategory_id = request.POST.get("subcategory")

        if not subcategory_id:
            messages.error(request, "Select Subcategory")
            return redirect("admin-products")

        fabric = request.POST.get("fabric")
        composition = request.POST.get("composition")
        sustainability = request.POST.get("sustainability")
        washing = request.POST.get("washing")
        # variant-mangement
        material_type = request.POST.get("material_type")


        category = get_object_or_404(Category,id=category_id)
        subcategory = get_object_or_404(Subcategory,id=subcategory_id)

        product = Product.objects.create(
            product_name = product_name,
            description_fit = description_fit,
            materials = fabric,
            care_guide = washing,
            category = category,
            subcategory = subcategory
        )


        images = request.FILES.getlist("images")

        for i, img in enumerate(images):
            ProductImage.objects.create(
                product = product,
                image = img,
                is_primary = True if i==0 else False
            )

        messages.success(request, "Product added")
        return redirect("admin-products")

    category_option = Category.objects.filter(is_deleted = False , is_active = True)


    return render(request, "product/add-product.html", {
        "category_option":category_option,

    })

def get_subcategories(request, category_id):
    subs = Subcategory.objects.filter(category_id=category_id, is_active = True , is_deleted = False)

    data = {
        "subcategories": list(subs.values("id", "subcategory_name"))
    }

    return JsonResponse(data)

def admin_product_details(request,id):

    product = get_object_or_404(Product, id=id)
    category = Category.objects.filter(is_active = True , is_deleted = False)
    subcatgory = Subcategory.objects.filter(is_active = True , is_deleted = False)

    if request.method == "POST":

        if request.POST.get("deleted_product"):
            product.is_deleted = True
            product.save()
            messages.success(request, "Product deleted succesfully")
            return redirect("admin-product")

        product_name = request.POST.get("product_name")
        category_id = request.POST.get("category")
        subcatgory_id = request.POST.get("subcategory")

        if not category_id or not subcatgory_id:
            messages.error(request, "Category and Subcategory are required")
            return redirect("admin-product-details", id=product.id)
        category_obj = get_object_or_404(Category, id=category_id)
        subcatgory_obj = get_object_or_404(Subcategory, id=subcatgory_id)


        if subcatgory_obj.category.id != category_obj.id:
            messages.error(request, "invalid subcategory for selected category")

            return render(request, "product/admin-product-details.html",{
                "product":product,
                "category": category,
                "subcategory": subcatgory
            })

        if request.FILES.get("image"):
            new_img = ProductImage.objects.create(
                product = product,
                image = request.FILES.get("image"),
                is_primary = False
            )

            if not ProductImage.objects.filter(product=product , is_primary=True).exists():
                new_img.is_primary = True
                new_img.save()

        primary_id = request.POST.get("primary_image")

        if primary_id:
            ProductImage.objects.filter(product=product).update(is_primary = False)
            ProductImage.objects.filter(id=primary_id , product=product).update(is_primary = True)

        delete_image_id = request.POST.get("deleted_image")

        if delete_image_id:
            image = ProductImage.objects.filter(id=delete_image_id , product=product).first()
            if image:
                image.delete()
            images = ProductImage.objects.filter(product=product)

            if not images.filter(is_primary=True).exists():
                first = images.first()
                if first:
                    first.is_primary = True
                    first.save()

            messages.success(request, "Image deleted successfully")
            return redirect("admin-product-details", id=product.id)

        is_active = request.POST.get("is_active")

        product.is_active = True if is_active == "on" else False


        materials = request.POST.get("materials")
        description_fit = request.POST.get("description_fit")
        care_guide = request.POST.get("care_guide")
        delivery_returns = request.POST.get("delivery_returns")

        product.product_name = product_name
        product.category = category_obj
        product.subcategory = subcatgory_obj
        product.materials = materials
        product.description_fit = description_fit
        product.care_guide = care_guide
        product.delivery_returns = delivery_returns

        product.save()
        messages.success(request, "Product updated")
        return redirect("admin-product-details", id=product.id)

    return render(request, "product/admin-product-details.html", {
        "product":product,
        "category": category,
        "subcategory":subcatgory
    })
