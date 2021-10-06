from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=32, null=True)

    def __str__(self) -> str:
        return str(self.name)


class Product(models.Model):
    link_to_image = models.URLField(null=True) # Can be an another model for different sizes
    name = models.CharField(max_length=32)
    price = models.FloatField()
    old_price = models.FloatField(null=True)
    amount_remaining = models.PositiveSmallIntegerField()
    description = models.TextField(max_length=1000)
    datetime_created = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )

    # Create seperated models for next two fields
    size = models.CharField(max_length=16)
    color = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f'{self.color} {self.name}, {self.size}'


class Review(models.Model):
    author_name = models.CharField(max_length=32)
    review_text = models.TextField(max_length=1000)
    like = models.BooleanField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.author_name}, ${self.product.name}, ${self.like}'
