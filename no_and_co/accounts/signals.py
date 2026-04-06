from allauth.account.signals import user_logged_in
from django.dispatch import receiver
from cart.views import merge_cart_after_login

@receiver(user_logged_in)
def merge_cart_google_login(request, user,**kwargs):
    
    old_session_key = request.session.get("pre_login_session_key")


    print("OLD GOOGLE SESSION:", old_session_key)
    print("CURRENT SESSION:", request.session.session_key)

    if not old_session_key:
        return

    merge_cart_after_login(request, user , old_session_key)

    request.session.pop("pre_login_session_key",None)
