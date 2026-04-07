from django.db.models import Sum
from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
    else:
        session_key = request.session.session_key
        if session_key:
            count = Cart.objects.filter(session_key=session_key).aggregate(total=Sum('quantity'))['total'] or 0
        else:
            count = 0
            
    return {'cart_count': count}
