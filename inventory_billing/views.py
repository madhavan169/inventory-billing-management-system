from django.shortcuts import render, redirect
from products.models import Product
from customers.models import Customer
from billing.models import Bill
from django.db import models
from purchases.models import Purchase, PurchaseReturn
from .forms import CustomUserCreationForm

from django.contrib.auth.decorators import (
    login_required,
    login_not_required
)

from django.contrib.auth.forms import UserCreationForm


@login_required(login_url='login')
def dashboard(request):

    total_products = Product.objects.count()

    total_customers = Customer.objects.count()

    low_stock_products = Product.objects.filter(
        stock__gt=0,
        stock__lte=5
    )

    low_stock_count = low_stock_products.count()

    out_of_stock_count = Product.objects.filter(
        stock=0
    ).count()

    total_sales = Bill.objects.aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    total_purchases = Purchase.objects.count()

    total_purchase_amount = Purchase.objects.aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    total_returns = PurchaseReturn.objects.count()

    total_return_amount = PurchaseReturn.objects.aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    paid_purchase_amount = Purchase.objects.filter(
        payment_status='Paid'
    ).aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    pending_purchase_amount = Purchase.objects.filter(
        payment_status='Pending'
    ).aggregate(
        total=models.Sum('total_amount')
    )['total'] or 0

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_sales': total_sales,
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_purchases': total_purchases,
        'total_purchase_amount': total_purchase_amount,
        'paid_purchase_amount': paid_purchase_amount,
        'pending_purchase_amount': pending_purchase_amount,
        'total_returns': total_returns,
        'total_return_amount': total_return_amount,
    }

    return render(request, 'dashboard.html', context)


@login_not_required
def register(request):

    if request.method == 'POST':

        form = CustomUserCreationForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('login')

    else:

        form = CustomUserCreationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )