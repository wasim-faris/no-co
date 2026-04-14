from django.shortcuts import render

def admin_returns(request):
    return render(request, "returns/returns.html")
