from django import forms
from .models import Bill


class BillForm(forms.ModelForm):

    class Meta:
        model = Bill
        fields = ['customer']


from products.models import Product
from .models import BillItem


class BillItemForm(forms.ModelForm):

    quantity = forms.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Quantity must be at least 1.',
            'required': 'Please enter quantity.'
        }
    )

    class BillItemForm(forms.ModelForm):

        product = forms.ModelChoiceField(
        queryset=Product.objects.filter(stock__gt=0),
        empty_label="Select Product"
    )

    quantity = forms.IntegerField(
        min_value=1,
        error_messages={
            'min_value': 'Quantity must be at least 1.',
            'required': 'Please enter quantity.'
        }
    )

    class Meta:
        model = BillItem
        fields = ['product', 'quantity']