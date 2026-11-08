
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ProductForm
from .models import Product
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from .models import Product, StockHistory

def add_product(request):

    if request.method == 'POST':

        form = ProductForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('add_product')

    else:

        form = ProductForm()

    return render(request, 'products/add_product.html', {
        'form': form
    })



def product_list(request):

    products = Product.objects.all()

    for product in products:

        if product.stock == 0:
            product.stock_status = 'Out of Stock'

        elif product.stock <= 5:
            product.stock_status = 'Low Stock'

        else:
            product.stock_status = 'In Stock'

    return render(request, 'products/product_list.html', {
        'products': products
    })


def update_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        old_stock = product.stock

        form = ProductForm(request.POST, instance=product)

        if form.is_valid():

            updated_product = form.save()

            new_stock = updated_product.stock

            if old_stock != new_stock:

                StockHistory.objects.create(
                    product=product,
                    old_stock=old_stock,
                    new_stock=new_stock
                )

            return redirect('product_list')

    else:
        form = ProductForm(instance=product)

    return render(request, 'products/update_product.html', {
        'form': form
    })




def stock_history(request):

    histories = StockHistory.objects.all().order_by('-changed_at')

    return render(request, 'products/stock_history.html', {
        'histories': histories
    })


def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully.')

        except ProtectedError:
            messages.error(
                request,
                'This product is already used in bills or purchases. '
                'You cannot delete this product.'
            )

        return redirect('product_list')

    return redirect('product_list')