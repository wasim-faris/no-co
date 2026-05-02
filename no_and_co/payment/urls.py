from django.urls import path
from . import views

urlpatterns = [
    # payment/<order_id>/ — matches view signature; named "payment-page" so
    # the existing redirect in core/views.py (redirect("payment-page")) works.
    path("payment/<int:order_id>/", views.payment, name="payment-page"),

    # Verify Razorpay signature — used by the frontend via fetch POST
    path("verify-payment/", views.verify_payment, name="verify-payment"),
    
    # Razorpay callback fallback
    path('payment/callback/', views.razorpay_callback, name='razorpay-callback'),
]
