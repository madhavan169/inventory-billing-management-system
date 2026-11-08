from django.db import models
from customers.models import Customer
from products.models import Product


class Bill(models.Model):


    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    date = models.DateTimeField(auto_now_add=True)

    PAYMENT_CHOICES = [
    ('Pending', 'Pending'),
    ('Paid', 'Paid'),]

    payment_status = models.CharField(
    max_length=20,
    choices=PAYMENT_CHOICES,
    default='Pending')

    def __str__(self):
        return f"Bill {self.id}"



class BillItem(models.Model):

    bill = models.ForeignKey(
        Bill,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return self.product.name

    @property
    def total_price(self):
        return self.quantity * self.price