from django.db import models

# Create your models here.
from django.db import models
from suppliers.models import Supplier
from products.models import Product


class Purchase(models.Model):

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT
    )

    purchase_date = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    PAYMENT_STATUS = [
    ('Pending', 'Pending'),
    ('Paid', 'Paid'),
]

    payment_status = models.CharField(
    max_length=20,
    choices=PAYMENT_STATUS,
    default='Pending'
)

    def __str__(self):
        return f"Purchase {self.id}"


class PurchaseItem(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    @property
    def total_price(self):
        return self.quantity * self.purchase_price

    def __str__(self):
        return self.product.name


    # Purchase Return

class PurchaseReturn(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.PROTECT
    )

    return_date = models.DateTimeField(
        auto_now_add=True
    )

    reason = models.TextField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"Return {self.id}"


class PurchaseReturnItem(models.Model):

    purchase_return = models.ForeignKey(
        PurchaseReturn,
        on_delete=models.CASCADE,
        related_name='items'
    )

    purchase_item = models.ForeignKey(
        PurchaseItem,
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()

    return_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    @property
    def total_price(self):
        return self.quantity * self.return_price

    def __str__(self):
        return self.purchase_item.product.name


class SupplierPayment(models.Model):

    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateTimeField(
        auto_now_add=True
    )

    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('Cash', 'Cash'),
            ('UPI', 'UPI'),
            ('Bank Transfer', 'Bank Transfer'),
        ]
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Payment for Purchase {self.purchase.id}"