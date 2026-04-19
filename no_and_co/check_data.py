import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'no_and_co.settings')
django.setup()

from wallet.models import WalletTransaction, Wallet

print("--- Wallet Transactions ---")
txns = WalletTransaction.objects.all().order_by('-created_at')[:10]
for t in txns:
    print(f"ID: {t.id}, Wallet: {t.wallet.user.username}, OrderID: {t.order_id}, Amount: {t.amount}, Desc: {t.description}")

print("\n--- Wallets ---")
wallets = Wallet.objects.all()
for w in wallets:
    print(f"User: {w.user.username}, Balance: {w.balance}")
