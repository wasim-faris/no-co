from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, ReturnRequest, Banner, HomepageVideo

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'total_amount', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    list_filter = ['payment_status', 'payment_method', 'created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'variant', 'quantity', 'price', 'item_status']
    list_filter = ['item_status']

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ['order', 'customer', 'reason', 'status', 'requested_at']
    list_filter = ['status', 'reason']

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']

@admin.register(HomepageVideo)
class HomepageVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'created_at']
    list_filter = ['is_active']

admin.site.register(OrderStatusHistory)
