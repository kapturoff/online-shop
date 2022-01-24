from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_service_id']


admin.site.register(Payment, PaymentAdmin)
