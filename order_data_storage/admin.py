from django.contrib import admin
from .models import Order, OrderItem, Transaction


class OrderItemAdmin(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemAdmin]

admin.site.register(Order, OrderAdmin)
admin.site.register(Transaction)
