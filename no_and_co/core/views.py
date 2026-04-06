from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.contrib.auth import login , logout
from users.decorators import block_check
from products.models import Variant, VariantImage,Product
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from category.models import Category,Subcategory
from django.db.models import Q
# Create your views here.

@never_cache
@block_check
def home(request):

    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin-dashboard")

    variants = Variant.objects.filter(is_default = True ,is_deleted = False, product__is_deleted = False).prefetch_related(
        Prefetch(
            "images",
            queryset = VariantImage.objects.filter(is_primary = True),
            to_attr= "primary_images"
        )
    ).order_by("-created_at")[:6]

    search_history = request.session.get("search_history",[])

    return render(request, "index.html",{
        "variants":variants,
        "search_history":search_history
    })

def ladies(request):
    search_history = request.session.get("search_history",[])
    return render(request, "ladies.html",{
        "search_history":search_history
    })

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
        rep_variant = p.variants.filter(is_active=True, is_deleted=False).order_by("-is_default", "id").first()
        if rep_variant:
            similar_items.append(rep_variant)


    product_image = None

    if default_variant:
        product_image = default_variant.images.filter(is_primary=True).first()
        if not product_image:
            product_image = default_variant.images.first()

    if not product_image:
        v_fallback = variants.first()
        if v_fallback:
            product_image = v_fallback.images.filter(is_primary=True).first()
            if not product_image:
                product_image = v_fallback.images.first()

    search_history = request.session.get("search_history",[])

    return render(request, "product-details.html",{
        "product":product,
        "variants":variants,
        "unique_variants":unique_variants,
        "unique_sizes":unique_sizes,
        "default_variant":default_variant,
        "product_image":product_image,
        "similar_items":similar_items,
        "search_history":search_history
    })

def product_listing(request):
    sort = request.GET.get("sort")
    subcategory = request.GET.get("subcategory")
    query = request.GET.get("q")
    action = request.GET.get("action")

    if action == "delete_history":

        request.session["search_history"] = []

    variants = Variant.objects.filter(
        product__is_active=True,
        product__is_deleted=False,
        is_default=True
    )

    if query:
        history = request.session.get("search_history",[])

        if query in history:
            history.remove(query)

        history.insert(0, query)

        history = history[:5]

        request.session["search_history"] = history

        variants = variants.filter(
            Q(product__product_name__icontains = query) | Q(product__description_fit__icontains = query)
        )

    if subcategory:
        subcategory = subcategory.upper()
        sub = get_object_or_404(Subcategory, subcategory_name=subcategory)
        variants = variants.filter(product__subcategory=sub)

    category_ref = request.GET.get("category")
    min_price = request.GET.get("price_min")
    max_price = request.GET.get("price_max")


    if min_price:
        variants = variants.filter(price__gte = min_price)

    if max_price:
        variants = variants.filter(price__lte = max_price)

    if category_ref:
        category_ref = category_ref.upper()
        category = get_object_or_404(Category, category_name = category_ref )
        variants = variants.filter(product__category = category)

    if sort == "newest":
        variants = variants.order_by("-id")
    elif sort == "lowest_price":
        variants = variants.order_by("price")
    elif sort == "highest_price":
        variants = variants.order_by("-price")
    elif sort == "name_asc":
        variants = variants.order_by("product__product_name")
    elif sort == "name_desc":
        variants = variants.order_by("-product__product_name")

    return render(request, "product-listing.html", {
        "variants": variants,
        "query":query,
        "search_history":request.session.get("search_history",[])
    })
