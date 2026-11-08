# Create your models here.
from django.db import models
class Product(models.Model):

    name = models.CharField(max_length=100)

    category = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField()

    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class StockHistory(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_history'
    )

    old_stock = models.PositiveIntegerField()

    new_stock = models.PositiveIntegerField()

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name