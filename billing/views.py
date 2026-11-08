from django.shortcuts import render, redirect, get_object_or_404
from .forms import BillForm, BillItemForm
from .models import Bill, BillItem
from decimal import Decimal
from django.db.models import Q

# Create New Bill

def create_bill(request):
    if request.method == 'POST':
        form = BillForm(request.POST)

        if form.is_valid():
            bill = form.save()
            return redirect('add_bill_item', bill_id=bill.id)

    else:
         form = BillForm()
 
    return render(request, 'billing/create_bill.html', {
    'form': form
})


# Add Products to Bill

def add_bill_item(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if request.method == 'POST':

        form = BillItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            if item.quantity > item.product.stock:
                form.add_error(
                'quantity',
                'Not enough stock available!'
            )

            else:
                existing_item = BillItem.objects.filter(
                bill=bill,
                product=item.product
            ).first()

                if existing_item:
                    existing_item.quantity += item.quantity
                    existing_item.save()

                else:
                    item.bill = bill
                    item.price = item.product.price
                    item.save()

            # Reduce product stock
                item.product.stock -= item.quantity
                item.product.save()

            # Calculate grand total
                total = sum(
                (
                    i.quantity * i.price
                    for i in bill.items.all()
                ),
                Decimal('0.00')
            )

            # Update bill total
                bill.total_amount = total
                bill.save(update_fields=['total_amount'])

                return redirect(
                'add_bill_item',
                bill_id=bill.id
            )

    else:
        form = BillItemForm()

# Get all bill items
    items = bill.items.all()

# Calculate individual item total
    for item in items:
        item.item_total = item.quantity * item.price

    return render(request, 'billing/add_bill_item.html', {
    'form': form,
    'bill': bill,
    'items': items})


# Bill History
def bill_history(request):

    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    bills = Bill.objects.all().order_by('-date')

    # Search by Bill ID or Customer Name
    if search:

        if search.isdigit():

            bills = bills.filter(
                Q(id=int(search)) |
                Q(customer__name__icontains=search)
            )

        else:

            bills = bills.filter(
                customer__name__icontains=search
            )

    # Filter by Payment Status
    if status in ['Paid', 'Pending']:
        bills = bills.filter(payment_status=status)

    # Filter by Start Date
    if start_date:
        bills = bills.filter(date__date__gte=start_date)

    # Filter by End Date
    if end_date:
        bills = bills.filter(date__date__lte=end_date)

    return render(request, 'billing/bill_history.html', {
        'bills': bills,
        'search': search,
        'status': status,
        'start_date': start_date,
        'end_date': end_date
    })
def bill_details(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)

    items = bill.items.all()

    for item in items:
        item.item_total = item.quantity * item.price
        return render(request, 'billing/bill_details.html', {
    'bill': bill,
    'items': items
})

# Update Payment Status

def update_payment_status(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    if request.method == 'POST':
        status = request.POST.get('payment_status')

        if status in dict(Bill.PAYMENT_CHOICES):
            bill.payment_status = status
            bill.save(update_fields=['payment_status'])

    return redirect('bill_history')


# Remove Product from Bill
def remove_bill_item(request, bill_id, item_id):

    bill = get_object_or_404(Bill, id=bill_id)

    if request.method == 'POST':

        bill_item = get_object_or_404(
            BillItem,
            id=item_id,
            bill=bill
        )

        # Restore product stock
        product = bill_item.product

        product.stock += bill_item.quantity
        product.save(update_fields=['stock'])

        # Delete bill item
        bill_item.delete()

        # Recalculate bill total
        total = sum(
            (
                item.quantity * item.price
                for item in bill.items.all()
            ),
            Decimal('0.00')
        )

        bill.total_amount = total
        bill.save(update_fields=['total_amount'])

    return redirect('add_bill_item', bill_id=bill.id)


# Billing Dashboard
def billing_dashboard(request):

    bills = Bill.objects.all()

    # Total Bills
    total_bills = bills.count()

    # Total Sales
    total_sales = sum(
        (bill.total_amount for bill in bills),
        Decimal('0.00')
    )

    # Paid Amount
    paid_amount = sum(
        (
            bill.total_amount
            for bill in bills
            if bill.payment_status == 'Paid'
        ),
        Decimal('0.00')
    )

    # Pending Amount
    pending_amount = sum(
        (
            bill.total_amount
            for bill in bills
            if bill.payment_status == 'Pending'
        ),
        Decimal('0.00')
    )
    # Get latest 5 bills
    recent_bills = bills.order_by('-date')[:5]

    return render(request, 'billing/billing_dashboard.html', {
        'total_bills': total_bills,
        'total_sales': total_sales,
        'paid_amount': paid_amount,
        'pending_amount': pending_amount,
        'recent_bills': recent_bills,
    })