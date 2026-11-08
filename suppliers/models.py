from django.db import models


class Supplier(models.Model):

    name = models.CharField(max_length=100)

    company_name = models.CharField(max_length=150)

    phone = models.CharField(max_length=15)

    email = models.EmailField(blank=True, null=True)

    address = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name