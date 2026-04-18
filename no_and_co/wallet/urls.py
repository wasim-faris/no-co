from django.urls import path
from . import views

urlpatterns = [
    path("wallet/", views.wallet, name="wallet"),
    path("wallet/create-order/", views.create_wallet_order),
    path("wallet/verify-payment/", views.verify_wallet_payment),
]
