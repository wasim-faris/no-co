from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
# Create your views here.

@never_cache
def home(request):
    return render(request, "index.html")
