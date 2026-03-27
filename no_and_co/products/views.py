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

    return render(request, "product/admin-product-details.html", {
        "product":product
    })
