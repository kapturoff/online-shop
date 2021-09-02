from products_data_storage.models import Product, Category
from django.db import models

# Create your models here.

class ParentCategory(models.Model):
    name = models.CharField(max_length=20)
    sub_categories = models.ManyToManyField(Category)

    def __str__(self) -> str:
        return self.name

class MainPageCarouselItem(models.Model):
    title = models.CharField(max_length=30)
    description = models.CharField(max_length=50)
    link_to_image = models.URLField(null=True)
    
    def __str__(self) -> str:
        return self.title