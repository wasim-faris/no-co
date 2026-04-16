from .models import Wishlist

def wishlist_count(request):
    if request.user.is_authenticated:
        count = Wishlist.objects.filter(user=request.user).count()
    else:
        session_key = request.session.session_key
        if session_key:
            count = Wishlist.objects.filter(session_key=session_key).count()
        else:
            count = 0
            
    return {'wishlist_count': count}
