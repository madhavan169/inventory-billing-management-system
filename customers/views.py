from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import CustomerForm
from django.db.models.deletion import ProtectedError
from django.contrib import messages

def add_customer(request):

    if request.method == 'POST':
        form = CustomerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('add_customer')

    else:
        form = CustomerForm()

    return render(request, 'customers/add_customer.html', {
        'form': form
    })

from .models import Customer


def customer_list(request):

    customers = Customer.objects.all()

    return render(request, 'customers/customer_list.html', {
        'customers': customers
    })


from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomerForm
from .models import Customer


def update_customer(request, id):

    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            return redirect('customer_list')

    else:
        form = CustomerForm(instance=customer)

    return render(request, 'customers/update_customer.html', {
        'form': form
    })


def delete_customer(request, id):
    customer = get_object_or_404(Customer, id=id)

    if request.method == 'POST':
        try:
            customer.delete()
            messages.success(
                request,
                'Customer deleted successfully.'
            )

        except ProtectedError:
            messages.error(
                request,
                'This customer is already used in bills. '
                'You cannot delete this customer.'
            )

        return redirect('customer_list')

    return redirect('customer_list')