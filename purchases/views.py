from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .forms import PurchaseForm, PurchaseItemForm
from .models import Purchase, PurchaseItem
from django.db.models import Q
from django.contrib import messages
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Q, Count
import csv
from django.http import HttpResponse
from django.contrib import messages
from products.models import StockHistory
from purchases.models import PurchaseReturn
from .models import SupplierPayment

from .forms import (
    PurchaseForm,
    PurchaseItemForm,
    PurchaseReturnForm,
    PurchaseReturnItemForm,
    SupplierPaymentForm
)

from .models import PurchaseReturn, PurchaseReturnItem
from .forms import PurchaseReturnForm, PurchaseReturnItemForm


# Create New Purchase

def create_purchase(request):

    if request.method == 'POST':

        form = PurchaseForm(request.POST)

        if form.is_valid():

            purchase = form.save()

            return redirect('add_purchase_items', id=purchase.id)

    else:

        form = PurchaseForm()

    return render(request, 'purchases/create_purchase.html', {
        'form': form
    })

# Add Products to Purchase

def add_purchase_items(request, id):

    purchase = get_object_or_404(Purchase, id=id)

    if request.method == 'POST':

        form = PurchaseItemForm(request.POST)

        if form.is_valid():

            item = form.save(commit=False)
            item.purchase = purchase
            item.save()

            # Increase Product Stock

            product = item.product
            old_stock = product.stock

            product.stock += item.quantity
            product.save()

            # Save Stock History

            from products.models import StockHistory

            StockHistory.objects.create(
                product=product,
                old_stock=old_stock,
                new_stock=product.stock
            )

            # Update Purchase Total

            purchase.total_amount += item.total_price
            purchase.save()

            return redirect('add_purchase_items', id=purchase.id)

    else:
        form = PurchaseItemForm()

    items = purchase.items.all()

    return render(request, 'purchases/add_purchase_items.html', {
        'purchase': purchase,
        'form': form,
        'items': items
    })
# Purchase List

def purchase_list(request):

    search = request.GET.get('search', '')

    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    purchases = Purchase.objects.all().order_by('-purchase_date')

    # Search Filter
    if search:
        if search.isdigit():
            purchases = purchases.filter(
                Q(supplier__name__icontains=search) |
                Q(id=int(search))
            )
        else:
            purchases = purchases.filter(
                supplier__name__icontains=search
            )

    # Start Date Filter
    if date_from:
        purchases = purchases.filter(
            purchase_date__date__gte=date_from
        )

    # End Date Filter
    if date_to:
        purchases = purchases.filter(
            purchase_date__date__lte=date_to
        )

    return render(request, 'purchases/purchase_list.html', {
        'purchases': purchases,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    })
# Purchase Details

def purchase_details(request, id):

    purchase = get_object_or_404(Purchase, id=id)

    items = purchase.items.all()
    # Supplier Payment History
    payments = purchase.payments.all().order_by('-payment_date')

    # Total Paid Amount
    paid_amount = purchase.payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Pending Amount
    pending_amount = purchase.total_amount - paid_amount

    context = {
        'purchase': purchase,
        'items': items,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'payments': payments,
    }

    return render(
        request,
        'purchases/purchase_details.html',
        context
    )
# Purchase Report

def purchase_report(request):

    total_purchases = Purchase.objects.count()

    total_amount = Purchase.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_products = PurchaseItem.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    paid_amount = Purchase.objects.filter(
        payment_status='Paid'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    pending_amount = Purchase.objects.filter(
        payment_status='Pending'
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    # Monthly Purchase Summary
    monthly_purchases = (
        Purchase.objects
        .annotate(month=TruncMonth('purchase_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('-month')
    )

    context = {
        'total_purchases': total_purchases,
        'total_amount': total_amount,
        'total_products': total_products,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'monthly_purchases': monthly_purchases,
    }

    return render(request, 'purchases/purchase_report.html', context)
# Update Purchase Payment Status

def update_payment_status(request, id):

    purchase = get_object_or_404(Purchase, id=id)

    if request.method == 'POST':

        status = request.POST.get('payment_status')

        if status in ['Paid', 'Pending']:
            purchase.payment_status = status
            purchase.save()

        return redirect('purchase_list')

def supplier_purchase_report(request):

    supplier_report = (
        Purchase.objects
        .values('supplier__name')
        .annotate(
            total_purchases=Count('id'),

            total_purchase_amount=Sum('total_amount'),

            paid_amount=Sum(
                'total_amount',
                filter=Q(payment_status='Paid')
            ),

            pending_amount=Sum(
                'total_amount',
                filter=Q(payment_status='Pending')
            )
        )
        .order_by('-total_purchase_amount')
    )
    total_outstanding = Purchase.objects.filter(
    payment_status='Pending'
).aggregate(
    total=Sum('total_amount')
)['total'] or 0

    context = {
        'supplier_report': supplier_report,
        'total_outstanding': total_outstanding,
    }

    return render(
        request,
        'purchases/supplier_purchase_report.html',
        context
    )
def remove_purchase_item(request, id):
    item = get_object_or_404(PurchaseItem, id=id)

    purchase = item.purchase
    product = item.product

    if request.method == 'POST':

        if product.stock < item.quantity:
            messages.error(
                request,
                'Cannot remove item. Available stock is insufficient.'
            )
            return redirect('purchase_details', id=purchase.id)

        old_stock = product.stock

        # Restore Stock
        product.stock -= item.quantity
        product.save()

        # Save Stock History
        from products.models import StockHistory

        StockHistory.objects.create(
            product=product,
            old_stock=old_stock,
            new_stock=product.stock
        )

        # Delete Purchase Item
        item.delete()

        # Recalculate Purchase Total
        purchase.total_amount = sum(
    item.total_price for item in purchase.items.all()
)

        purchase.save()

        return redirect('purchase_details', id=purchase.id)

    return redirect('purchase_details', id=purchase.id)


def export_purchases(request):

    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    purchases = Purchase.objects.all().order_by('-purchase_date')

    # Search Purchase ID or Supplier Name
    if search:
        if search.isdigit():
            purchases = purchases.filter(
                Q(supplier__name__icontains=search) |
                Q(id=int(search))
            )
        else:
            purchases = purchases.filter(
                supplier__name__icontains=search
            )

    # From Date Filter
    if date_from:
        purchases = purchases.filter(
            purchase_date__date__gte=date_from
        )

    # To Date Filter
    if date_to:
        purchases = purchases.filter(
            purchase_date__date__lte=date_to
        )

    # CSV Response
    response = HttpResponse(
        content_type='text/csv'
    )

    response['Content-Disposition'] = (
        'attachment; filename="purchase_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        'Purchase ID',
        'Supplier',
        'Purchase Date',
        'Total Amount',
        'Payment Status'
    ])

    for purchase in purchases:

        writer.writerow([
            purchase.id,
            purchase.supplier.name,
            purchase.purchase_date,
            purchase.total_amount,
            purchase.payment_status
        ])

    return response


# Edit Purchase

def edit_purchase(request, id):

    purchase = get_object_or_404(Purchase, id=id)

    if request.method == 'POST':

        form = PurchaseForm(request.POST, instance=purchase)

        if form.is_valid():
            form.save()

            return redirect('purchase_list')

    else:

        form = PurchaseForm(instance=purchase)

    return render(request, 'purchases/edit_purchase.html', {
        'form': form,
        'purchase': purchase
    })


# Delete Purchase

def delete_purchase(request, id):

    purchase = get_object_or_404(Purchase, id=id)

    if request.method == 'POST':

        items = purchase.items.all()

        # Check stock before deleting
        for item in items:

            if item.product.stock < item.quantity:

                messages.error(
                    request,
                    f'Cannot delete purchase. Insufficient stock for {item.product.name}.'
                )

                return redirect('purchase_details', id=purchase.id)

        # Reduce stock
        for item in items:

            product = item.product

            old_stock = product.stock

            product.stock -= item.quantity

            product.save()

            StockHistory.objects.create(
                product=product,
                old_stock=old_stock,
                new_stock=product.stock
            )

        purchase.delete()

        return redirect('purchase_list')

    return redirect('purchase_list')


# Create Purchase Return

def create_purchase_return(request):

    if request.method == 'POST':

        form = PurchaseReturnForm(request.POST)

        if form.is_valid():

            purchase_return = form.save()

            return redirect(
                'add_purchase_return_items',
                id=purchase_return.id
            )

    else:

        form = PurchaseReturnForm()

    return render(
        request,
        'purchases/create_purchase_return.html',
        {'form': form}
    )


# Add Purchase Return Items

def add_purchase_return_items(request, id):

    purchase_return = get_object_or_404(PurchaseReturn, id=id)

    if request.method == 'POST':

        form = PurchaseReturnItemForm(
            request.POST,
            purchase=purchase_return.purchase
        )

        if form.is_valid():

            item = form.save(commit=False)

            purchase_item = item.purchase_item
            product = purchase_item.product

            already_returned = PurchaseReturnItem.objects.filter(
                purchase_item=purchase_item
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0

            remaining_quantity = (
                purchase_item.quantity - already_returned
            )

            if item.quantity < 1:
                messages.error(request, 'Quantity must be at least 1.')

            elif item.quantity > remaining_quantity:
                messages.error(
                    request,
                    f'Only {remaining_quantity} quantity can be returned.'
                )

            elif item.quantity > product.stock:
                messages.error(
                    request,
                    'Insufficient stock for this return.'
                )

            else:

                old_stock = product.stock

                product.stock -= item.quantity
                product.save()

                StockHistory.objects.create(
                    product=product,
                    old_stock=old_stock,
                    new_stock=product.stock
                )

                item.purchase_return = purchase_return
                item.save()

                purchase_return.total_amount += item.total_price
                purchase_return.save()

                messages.success(
                    request,
                    'Purchase return item added successfully.'
                )

                return redirect(
                    'add_purchase_return_items',
                    id=id
                )

    else:

        form = PurchaseReturnItemForm(
            purchase=purchase_return.purchase
        )

    return render(
        request,
        'purchases/add_purchase_return_items.html',
        {
            'form': form,
            'purchase_return': purchase_return
        }
    )
# Purchase Return History

# Purchase Return History with Search and Filter

def purchase_return_list(request):

    search = request.GET.get('search', '')

    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    returns = PurchaseReturn.objects.all().order_by('-return_date')

    # Search by Return ID or Supplier Name
    if search:

        if search.isdigit():

            returns = returns.filter(
                Q(id=int(search)) |
                Q(purchase__supplier__name__icontains=search)
            )

        else:

            returns = returns.filter(
                purchase__supplier__name__icontains=search
            )

    # Date From Filter
    if date_from:

        returns = returns.filter(
            return_date__date__gte=date_from
        )

    # Date To Filter
    if date_to:

        returns = returns.filter(
            return_date__date__lte=date_to
        )

    total_returns = returns.count()

    total_return_amount = returns.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    context = {
        'returns': returns,
        'total_returns': total_returns,
        'total_return_amount': total_return_amount,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(
        request,
        'purchases/purchase_return_list.html',
        context
    )

# Purchase Return Details

def purchase_return_details(request, id):

    purchase_return = get_object_or_404(
        PurchaseReturn,
        id=id
    )

    return_items = purchase_return.items.all()

    context = {
        'purchase_return': purchase_return,
        'return_items': return_items,
    }

    return render(
        request,
        'purchases/purchase_return_details.html',
        context
    )
# Purchase Return Report

def purchase_return_report(request):

    total_returns = PurchaseReturn.objects.count()

    total_return_amount = PurchaseReturn.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_return_products = PurchaseReturnItem.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    monthly_returns = (
        PurchaseReturn.objects
        .annotate(month=TruncMonth('return_date'))
        .values('month')
        .annotate(total=Sum('total_amount'))
        .order_by('-month')
    )

    context = {
        'total_returns': total_returns,
        'total_return_amount': total_return_amount,
        'total_return_products': total_return_products,
        'monthly_returns': monthly_returns,
    }

    return render(
        request,
        'purchases/purchase_return_report.html',
        context
    )


# Export Purchase Returns CSV

# Export Filtered Purchase Returns CSV

def export_purchase_returns(request):

    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    returns = PurchaseReturn.objects.all().order_by('-return_date')

    # Search Filter
    if search:

        if search.isdigit():

            returns = returns.filter(
                Q(id=int(search)) |
                Q(purchase__supplier__name__icontains=search)
            )

        else:

            returns = returns.filter(
                purchase__supplier__name__icontains=search
            )

    # From Date
    if date_from:

        returns = returns.filter(
            return_date__date__gte=date_from
        )

    # To Date
    if date_to:

        returns = returns.filter(
            return_date__date__lte=date_to
        )

    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = (
        'attachment; filename="purchase_return_report.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        'Return ID',
        'Purchase ID',
        'Supplier',
        'Return Date',
        'Reason',
        'Product',
        'Quantity',
        'Return Price',
        'Total Amount'
    ])

    for purchase_return in returns:

        for item in purchase_return.items.all():

            writer.writerow([
                purchase_return.id,
                purchase_return.purchase.id,
                purchase_return.purchase.supplier.name,
                purchase_return.return_date,
                purchase_return.reason,
                item.purchase_item.product.name,
                item.quantity,
                item.return_price,
                item.total_price
            ])

    return response



# Delete Purchase Return

def delete_purchase_return(request, id):

    purchase_return = get_object_or_404(
        PurchaseReturn,
        id=id
    )

    if request.method == 'POST':

        return_items = purchase_return.items.all()

        # Restore Product Stock
        for item in return_items:

            product = item.purchase_item.product

            old_stock = product.stock

            product.stock += item.quantity

            product.save()

            # Stock History
            StockHistory.objects.create(
                product=product,
                old_stock=old_stock,
                new_stock=product.stock
            )

        # Delete Return
        purchase_return.delete()

        return redirect('purchase_return_list')

    return redirect('purchase_return_list')

def edit_purchase_return(request, id):

    purchase_return = get_object_or_404(
        PurchaseReturn,
        id=id
    )

    if request.method == 'POST':

        form = PurchaseReturnForm(
            request.POST,
            instance=purchase_return
        )

        if form.is_valid():
            form.save()

            return redirect(
                'purchase_return_details',
                id=purchase_return.id
            )

    else:
        form = PurchaseReturnForm(
            instance=purchase_return
        )

    return render(
        request,
        'purchases/edit_purchase_return.html',
        {
            'form': form,
            'purchase_return': purchase_return
        }
    )

def edit_purchase_return_item(request, id):

    item = get_object_or_404(PurchaseReturnItem, id=id)

    purchase_return = item.purchase_return
    product = item.purchase_item.product
    purchase_item = item.purchase_item

    if request.method == 'POST':

        form = PurchaseReturnItemForm(
            request.POST,
            instance=item
        )

        form.fields['purchase_item'].disabled = True

        if form.is_valid():

            updated_quantity = form.cleaned_data['quantity']
            old_quantity = item.quantity

            # Other return quantities
            other_returns = PurchaseReturnItem.objects.filter(
                purchase_item=purchase_item
            ).exclude(
                id=item.id
            ).aggregate(
                total=Sum('quantity')
            )['total'] or 0

            # Maximum allowed return quantity
            remaining_quantity = purchase_item.quantity - other_returns

            if updated_quantity > remaining_quantity:

                messages.error(
                    request,
                    f'You can return maximum {remaining_quantity} quantity.'
                )

            else:

                difference = updated_quantity - old_quantity

                if difference > 0 and product.stock < difference:

                    messages.error(
                        request,
                        'Insufficient stock available.'
                    )

                else:

                    old_stock = product.stock

                    product.stock -= difference
                    product.save()

                    if old_stock != product.stock:

                        StockHistory.objects.create(
                            product=product,
                            old_stock=old_stock,
                            new_stock=product.stock
                        )

                    form.save()

                    purchase_return.total_amount = sum(
                        return_item.total_price
                        for return_item in purchase_return.items.all()
                    )

                    purchase_return.save()

                    return redirect(
                        'purchase_return_details',
                        id=purchase_return.id
                    )

    else:

        form = PurchaseReturnItemForm(instance=item)
        form.fields['purchase_item'].disabled = True

    return render(
        request,
        'purchases/edit_purchase_return_item.html',
        {
            'form': form,
            'item': item
        }
    )

def delete_purchase_return_item(request, id):

    item = get_object_or_404(PurchaseReturnItem, id=id)

    purchase_return = item.purchase_return
    product = item.purchase_item.product

    if request.method == 'POST':

        # Restore Product Stock
        old_stock = product.stock

        product.stock += item.quantity
        product.save()

        # Save Stock History
        StockHistory.objects.create(
            product=product,
            old_stock=old_stock,
            new_stock=product.stock
        )

        # Delete Return Item
        item.delete()

        # Recalculate Return Amount
        purchase_return.total_amount = sum(
            return_item.total_price
            for return_item in purchase_return.items.all()
        )

        purchase_return.save()

        return redirect(
            'purchase_return_details',
            id=purchase_return.id
        )

    return redirect(
        'purchase_return_details',
        id=purchase_return.id
    )

def add_supplier_payment(request, id):

    purchase = get_object_or_404(Purchase, id=id)

    paid_amount = purchase.payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    pending_amount = purchase.total_amount - paid_amount

    if request.method == 'POST':

        form = SupplierPaymentForm(request.POST)

        if form.is_valid():

            payment = form.save(commit=False)

            amount = payment.amount

            if amount <= 0:

                messages.error(
                    request,
                    'Payment amount must be greater than zero.'
                )

            elif amount > pending_amount:

                messages.error(
                    request,
                    f'Only ₹{pending_amount} is pending.'
                )

            else:

                payment.purchase = purchase
                payment.save()

                paid_amount = purchase.payments.aggregate(
                    total=Sum('amount')
                )['total'] or 0

                pending_amount = purchase.total_amount - paid_amount

                if pending_amount <= 0:
                    purchase.payment_status = 'Paid'
                else:
                    purchase.payment_status = 'Pending'

                purchase.save()

                messages.success(
                    request,
                    'Supplier payment added successfully.'
                )

                return redirect(
                    'purchase_details',
                    id=purchase.id
                )

    else:
        form = SupplierPaymentForm()

    return render(
        request,
        'purchases/add_supplier_payment.html',
        {
            'form': form,
            'purchase': purchase,
            'pending_amount': pending_amount,
        }
    )


def supplier_payment_list(request):

    # Search
    search = request.GET.get('search', '')

    # Date Filter
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Get All Payments
    payments = SupplierPayment.objects.all().order_by('-payment_date')

    # Search by Supplier Name or Purchase ID
    if search:
        if search.isdigit():
            payments = payments.filter(
                Q(purchase__supplier__name__icontains=search) |
                Q(purchase__id=int(search))
            )
        else:
            payments = payments.filter(
                purchase__supplier__name__icontains=search
            )

    # From Date Filter
    if date_from:
        payments = payments.filter(
            payment_date__date__gte=date_from
        )

    # To Date Filter
    if date_to:
        payments = payments.filter(
            payment_date__date__lte=date_to
        )

    # Calculate Total Paid Amount
    total_paid = payments.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Context
    context = {
        'payments': payments,
        'total_paid': total_paid,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(
        request,
        'purchases/supplier_payment_list.html',
        context
    )


def export_supplier_payments(request):

    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    payments = SupplierPayment.objects.all().order_by('-payment_date')

    # Search Filter
    if search:
        if search.isdigit():
            payments = payments.filter(
                Q(purchase__supplier__name__icontains=search) |
                Q(purchase__id=int(search))
            )
        else:
            payments = payments.filter(
                purchase__supplier__name__icontains=search
            )

    # From Date Filter
    if date_from:
        payments = payments.filter(
            payment_date__date__gte=date_from
        )

    # To Date Filter
    if date_to:
        payments = payments.filter(
            payment_date__date__lte=date_to
        )

    # Create CSV Response
    response = HttpResponse(
        content_type='text/csv'
    )

    response['Content-Disposition'] = (
        'attachment; filename="supplier_payments.csv"'
    )

    writer = csv.writer(response)

    # CSV Headings
    writer.writerow([
        'Payment ID',
        'Purchase ID',
        'Supplier Name',
        'Amount',
        'Payment Method',
        'Payment Date',
        'Notes'
    ])

    # Payment Data
    for payment in payments:

        writer.writerow([
            payment.id,
            payment.purchase.id,
            payment.purchase.supplier.name,
            payment.amount,
            payment.payment_method,
            payment.payment_date,
            payment.notes
        ])

    return response



def edit_supplier_payment(request, id):

    payment = get_object_or_404(SupplierPayment, id=id)
    purchase = payment.purchase

    if request.method == 'POST':

        form = SupplierPaymentForm(
            request.POST,
            instance=payment
        )

        if form.is_valid():

            updated_payment = form.save(commit=False)

            # Calculate other payments excluding current payment
            other_paid = purchase.payments.exclude(
                id=payment.id
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            pending_amount = purchase.total_amount - other_paid

            # Validate payment amount
            if updated_payment.amount <= 0:

                messages.error(
                    request,
                    'Payment amount must be greater than zero.'
                )

            elif updated_payment.amount > pending_amount:

                messages.error(
                    request,
                    f'Only ₹{pending_amount} is pending.'
                )

            else:

                updated_payment.purchase = purchase
                updated_payment.save()

                # Recalculate total paid amount
                total_paid = purchase.payments.aggregate(
                    total=Sum('amount')
                )['total'] or 0

                if total_paid >= purchase.total_amount:
                    purchase.payment_status = 'Paid'
                else:
                    purchase.payment_status = 'Pending'

                purchase.save()

                messages.success(
                    request,
                    'Supplier payment updated successfully.'
                )

                return redirect('purchase_details', id=purchase.id)

    else:

        form = SupplierPaymentForm(instance=payment)

    return render(
        request,
        'purchases/edit_supplier_payment.html',
        {
            'form': form,
            'payment': payment,
            'purchase': purchase,
        }
    )

def delete_supplier_payment(request, id):

    payment = get_object_or_404(SupplierPayment, id=id)
    purchase = payment.purchase

    if request.method == 'POST':

        payment.delete()

        # Recalculate Total Paid Amount
        total_paid = purchase.payments.aggregate(
            total=Sum('amount')
        )['total'] or 0

        # Update Payment Status
        if total_paid >= purchase.total_amount:
            purchase.payment_status = 'Paid'
        else:
            purchase.payment_status = 'Pending'

        purchase.save()

        messages.success(
            request,
            'Supplier payment deleted successfully.'
        )

        return redirect('supplier_payment_list')

    return render(
        request,
        'purchases/delete_supplier_payment.html',
        {
            'payment': payment,
            'purchase': purchase,
        }
    )
def supplier_payment_report(request):

    # Total Payment Count
    total_payments = SupplierPayment.objects.count()

    # Total Paid Amount
    total_paid = SupplierPayment.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Payment Method Wise Report
    payment_methods = (
        SupplierPayment.objects
        .values('payment_method')
        .annotate(
            total_amount=Sum('amount'),
            payment_count=Count('id')
        )
        .order_by('payment_method')
    )

    # Cash Total
    cash_total = SupplierPayment.objects.filter(
        payment_method='Cash'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # UPI Total
    upi_total = SupplierPayment.objects.filter(
        payment_method='UPI'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Bank Transfer Total
    bank_total = SupplierPayment.objects.filter(
        payment_method='Bank Transfer'
    ).aggregate(
        total=Sum('amount')
    )['total'] or 0

    context = {
        'total_payments': total_payments,
        'total_paid': total_paid,
        'cash_total': cash_total,
        'upi_total': upi_total,
        'bank_total': bank_total,
        'payment_methods': payment_methods,
    }

    return render(
        request,
        'purchases/supplier_payment_report.html',
        context
    )


def supplier_payment_receipt(request, id):

    payment = get_object_or_404(
        SupplierPayment,
        id=id
    )

    context = {
        'payment': payment,
        'purchase': payment.purchase,
        'supplier': payment.purchase.supplier,
    }

    return render(
        request,
        'purchases/supplier_payment_receipt.html',
        context
    )