from django.contrib import admin
from .models import Order, OrderItem, OrderStatus


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemAdmin]

class OrderTabularAdmin(admin.TabularInline):
    model = Order

class OrderStatusAdmin(admin.ModelAdmin):
    inlines = [OrderTabularAdmin]


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderStatus, OrderStatusAdmin)
