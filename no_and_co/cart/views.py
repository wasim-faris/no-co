from django.shortcuts import render


def cart_view(request):
    return render(request, 'cart.html')

def add_to_cart(request):
    pass
