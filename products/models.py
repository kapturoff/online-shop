from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=32, null=True)

    def __str__(self) -> str:
        return str(self.name)


class Product(models.Model):
    img = models.URLField(null=True)
    name = models.CharField(max_length=32)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    old_price = models.FloatField(null=True)
    amount_remaining = models.PositiveSmallIntegerField()
    description = models.TextField(max_length=1000)
    datetime_created = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )

    # TODO: Create seperated models for next two fields (#a36f5667)
    size = models.CharField(max_length=16)
    color = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f'{self.color} {self.name}, {self.size}'


class Review(models.Model):
    author_name = models.CharField(max_length=32)
    review_text = models.TextField(max_length=1000)
    liked = models.BooleanField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'{self.author_name}, ${self.product.name}, ${self.like}'
