from django.contrib import admin
from .models import Order, OrderItem


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemAdmin]

class OrderTabularAdmin(admin.TabularInline):
    model = Order

admin.site.register(Order, OrderAdmin)
