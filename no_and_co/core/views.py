from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import login , logout
from users.decorators import block_check
from products.models import Variant, VariantImage,Product
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
# Create your views here.

@never_cache
@block_check
def home(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    variants = Variant.objects.filter(is_default = True).prefetch_related(
        Prefetch(
            "images",
            queryset = VariantImage.objects.filter(is_primary = True),
            to_attr= "primary_images"
        )
    ).order_by("-created_at")[:6]

    return render(request, "index.html",{
        "variants":variants
    })

def ladies(request):
    return render(request, "ladies.html")

def product_details(request, id):
    product = get_object_or_404(Product , id=id)

    variants = product.variants.filter(is_active=True, is_deleted=False).prefetch_related(
        Prefetch(
            "images",
            queryset=VariantImage.objects.filter(is_primary=True),
            to_attr="primary_images"
        ),
        "images"
    ).order_by("-is_default", "id")
    default_variant = variants.first()

    unique_variants = []
    seen_colors = set()

    for i in variants:
        if i.color not in seen_colors:
            unique_variants.append(i)
            seen_colors.add(i.color)

    unique_sizes = []
    seen_sizes = set()

    for i in variants:
        size_name = i.size.name

        if size_name not in seen_sizes:
            unique_sizes.append(i)
            seen_sizes.add(size_name)

    similar_products = Product.objects.filter(is_active=True, is_deleted=False).exclude(id=product.id).order_by('-created_at')[:6]
    similar_items = []
    for p in similar_products:
        rep_variant = p.variants.filter(is_active=True, is_deleted=False).order_by('-is_default', 'id').first()
        if rep_variant:
            similar_items.append(rep_variant)

    return render(request, "product-details.html",{
        "product":product,
        "variants":variants,
        "unique_variants":unique_variants,
        "unique_sizes":unique_sizes,
        "default_variant":default_variant,
        "similar_items":similar_items
    })
