from django.contrib import admin
from .models import Category, Product


class ProductAdmin(admin.TabularInline):
    model = Product


class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductAdmin]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product)
