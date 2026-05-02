from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import get_user_model

User = get_user_model()

def block_check(view_func):
    def wrapper(request , *args, **kwargs):
        
        if request.user.is_authenticated:
            try:
                user = User.objects.get(id=request.user.id)
                if user.is_blocked:
                    messages.error(request, "currently you are blocked")
                    logout(request)
                    return redirect("home")
            except User.DoesNotExist:
                pass
        return view_func(request, *args, **kwargs)
    return wrapper
