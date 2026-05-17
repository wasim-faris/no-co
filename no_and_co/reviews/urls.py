from django.urls import path
from . import views

urlpatterns = [
    path("review/submit/", views.submit_review, name="submit-review"),
    path("api/reviews/product/<int:product_id>/", views.product_reviews_api, name="product-reviews-api"),
    path("admin-reviews/", views.admin_reviews_list, name="admin-reviews"),
    path("admin-reviews/<int:review_id>/status/", views.admin_review_status, name="admin-review-status"),
]
