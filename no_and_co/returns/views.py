from django.shortcuts import render, redirect
from core.models import ReturnRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
def admin_returns(request):
    return_requests = ReturnRequest.objects.all()
    return render(request, "returns/returns.html", {
        "return_requests":return_requests
    })

def approve_return(request):
    if request.method == "POST":
        return_request_id = request.POST.get("return_request_id")

        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        return_request.status = "APPROVED"
        return_request.approved_at = timezone.now()
        return_request.save()

        order_item = return_request.order_item
        order_item.item_status = "RETURN_APPROVED"
        order_item.save()

        messages.success(request, "return request approved succesfully")
    return redirect("admin-returns")

def reject_return(request):
    if request.method == "POST":

        return_request_id = request.POST.get("return_request_id")
        return_request = get_object_or_404(ReturnRequest, id=return_request_id)

        return_request.status = "REJECTED"
        return_request.rejected_at = timezone.now()
        return_request.save()

        order_item = return_request.order_item
        order_item.item_status = 'DELIVERED'
        order_item.save()

        messages.error(request, "return request rejected")

    return redirect("admin-return")
