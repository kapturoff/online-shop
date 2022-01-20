from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=32, null=True)

    def __str__(self) -> str:
        return str(self.name)


class Product(models.Model):
    img = models.URLField(blank=True, default=None)
    name = models.CharField(max_length=32)
    price = models.DecimalField(decimal_places=2, max_digits=7)
    old_price = models.FloatField(blank=True, default=0)
    amount_remaining = models.PositiveSmallIntegerField()
    description = models.TextField(max_length=1000)
    datetime_created = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
    )

    @property
    def reviews_count(self):
        return Review.objects.filter(product__id=self.id).count()

    @property
    def likes_count(self):
        return Review.objects.filter(product__id=self.id, liked=True).count()

    @property
    def dislikes_count(self):
        return Review.objects.filter(product__id=self.id, liked=False).count()

    # TODO: Create seperated models for next two fields (#a36f5667)
    size = models.CharField(max_length=16)
    color = models.CharField(max_length=32)

    def __str__(self) -> str:
        return f'{self.color} {self.name}, {self.size}'


class Review(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='commentaries',
        blank=True,
        default=None
    )
    liked = models.BooleanField()
    review_text = models.TextField(max_length=1000)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f'#{self.id}: {self.product.name}, {self.author.username}'
