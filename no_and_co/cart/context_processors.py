from .models import Cart

def cart_count(request):
    if request.user.is_authenticated:
        count = Cart.objects.filter(user=request.user).count()
    else:
        session_key = request.session.session_key
        if session_key:
            count = Cart.objects.filter(session_key=session_key).count()
        else:
            count = 0
            
    return {'cart_count': count}
