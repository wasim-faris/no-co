from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from admin_dashboard.decorators import admin_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from .models import Review
from core.models import Order, OrderItem
from products.models import Product


@login_required(login_url="login")
def submit_review(request):
    if request.method == "POST":
        product_id = request.POST.get("productId")
        order_id = request.POST.get("orderId")
        rating = request.POST.get("rating")
        description = request.POST.get("description", "").strip()
        
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            return JsonResponse({"success": False, "error": "Invalid rating."}, status=400)
            
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            product = Product.objects.get(id=product_id)
        except (Order.DoesNotExist, Product.DoesNotExist):
            return JsonResponse({"success": False, "error": "Invalid request."}, status=400)
        
        # Check if already reviewed
        if Review.objects.filter(user=request.user, product=product, order=order).exists():
            return JsonResponse({"success": False, "error": "You have already reviewed this product for this order."}, status=400)
            
        # Get delivered item
        order_item = order.items.filter(variant__product=product, item_status="DELIVERED").first()
        if not order_item:
            return JsonResponse({"success": False, "error": "You can only review products that have been delivered."}, status=400)
            
        # Images are optional
        images = request.FILES.getlist("images")
        if len(images) > 3:
            return JsonResponse({"success": False, "error": "You can only upload a maximum of 3 images."}, status=400)
            
        review = Review(
            user=request.user,
            product=product,
            order=order,
            order_item=order_item,
            rating=rating,
            description=description
        )
        
        if len(images) > 0:
            review.image1 = images[0]
        if len(images) > 1:
            review.image2 = images[1]
        if len(images) > 2:
            review.image3 = images[2]
            
        review.save()
        return JsonResponse({"success": True, "message": "Review submitted successfully! It will be visible once approved."})
        
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

def product_reviews_api(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product, status="approved").select_related("user").order_by("-created_at")
    
    agg = reviews.aggregate(avg_rating=Avg('rating'), count=Count('id'))
    
    reviews_data = []
    for r in reviews:
        images = []
        if r.image1: images.append(r.image1.url)
        if r.image2: images.append(r.image2.url)
        if r.image3: images.append(r.image3.url)
        
        reviews_data.append({
            "id": r.id,
            "username": r.user.get_full_name() or r.user.username,
            "rating": r.rating,
            "description": r.description,
            "date": r.created_at.strftime("%B %d, %Y"),
            "images": images
        })
        
    return JsonResponse({
        "avg_rating": round(agg["avg_rating"] or 0, 1),
        "count": agg["count"],
        "reviews": reviews_data
    })

@admin_required
def admin_reviews_list(request):
    status_filter = request.GET.get("status", "all")
    
    reviews = Review.objects.all().select_related("user", "product")
    
    if status_filter in ["pending", "approved", "rejected"]:
        reviews = reviews.filter(status=status_filter)
        
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "reviews/admin_reviews.html", {
        "page_obj": page_obj,
        "status_filter": status_filter
    })

@admin_required
def admin_review_status(request, review_id):
    if request.method == "POST":
        status = request.POST.get("status")
        if status in ["approved", "rejected"]:
            review = get_object_or_404(Review, id=review_id)
            review.status = status
            review.save()
            messages.success(request, f"Review {status} successfully.")
            
    # redirect back to referrer if available
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect("admin-reviews")
