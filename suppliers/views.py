from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect,get_object_or_404
from .forms import SupplierForm
from .models import Supplier

def add_supplier(request):

    if request.method == 'POST':

        form = SupplierForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('add_supplier')

    else:

        form = SupplierForm()

    return render(request, 'suppliers/add_supplier.html', {
        'form': form
    })

def supplier_list(request):
    suppliers = Supplier.objects.all().order_by('-created_at')

    return render(request, 'suppliers/supplier_list.html', {
        'suppliers': suppliers
    })

def update_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)

        if form.is_valid():
            form.save()
            return redirect('supplier_list')

    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'suppliers/update_supplier.html', {
        'form': form
    })

def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)

    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')

    return render(request, 'suppliers/delete_supplier.html', {
        'supplier': supplier
    })