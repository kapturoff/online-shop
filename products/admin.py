from xml.etree.ElementInclude import include
from django.contrib import admin
from .models import Category, Product, Review


class ProductAdmin(admin.TabularInline):
    model = Product


class CategoryAdmin(admin.ModelAdmin):
    inlines = [ProductAdmin]


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'amount_remaining', 'color', 'size', 'reviews_count',
        'likes_count', 'dislikes_count'
    )

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'product', 'liked',)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Review, ReviewAdmin)
