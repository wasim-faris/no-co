from django.shortcuts import render

# DUMMY DATA FOR STATIC UI DEMONSTRATION
DUMMY_TRANSACTIONS = [
    {
        'date_time': 'Oct 24, 2023, 02:30 PM',
        'transaction_id': 'TXN102948576',
        'order_id': 'ORD-99281',
        'description': 'Purchase: Linen Blend Shirt',
        'status': 'SUCCESS',
        'amount': '- ₹1,499.00'
    },
    {
        'date_time': 'Oct 22, 2023, 11:15 AM',
        'transaction_id': 'TXN102948500',
        'order_id': 'ORD-99150',
        'description': 'Refund: Oversized Cotton Tee',
        'status': 'REFUND',
        'amount': '+ ₹899.00'
    },
    {
        'date_time': 'Oct 20, 2023, 09:45 AM',
        'transaction_id': 'TXN102948420',
        'order_id': None,
        'description': 'Wallet Recharge',
        'status': 'SUCCESS',
        'amount': '+ ₹5,000.00'
    },
    {
        'date_time': 'Oct 15, 2023, 04:20 PM',
        'transaction_id': 'TXN102948300',
        'order_id': 'ORD-98800',
        'description': 'Purchase: Slim Fit Chinos',
        'status': 'SUCCESS',
        'amount': '- ₹2,299.00'
    },
    {
        'date_time': 'Oct 10, 2023, 01:10 PM',
        'transaction_id': 'TXN102948150',
        'order_id': 'ORD-98550',
        'description': 'Purchase: Premium Leather Belt',
        'status': 'SUCCESS',
        'amount': '- ₹1,199.00'
    },
]

def wallet(request):
    """
    Renders a static Wallet page with dummy data.
    No database queries or models are used as per requirements.
    """
    context = {
        'balance': '12,450.00',
        'transactions': DUMMY_TRANSACTIONS,
    }
    return render(request, 'wallet/wallet.html', context)
