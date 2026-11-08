from django import forms
from .models import Purchase, PurchaseItem
from .models import SupplierPayment

class PurchaseForm(forms.ModelForm):

    class Meta:
        model = Purchase
        fields = ['supplier']


class PurchaseItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseItem
        fields = ['product', 'quantity', 'purchase_price']


from .models import PurchaseReturn, PurchaseReturnItem


class PurchaseReturnForm(forms.ModelForm):

    class Meta:
        model = PurchaseReturn
        fields = ['purchase', 'reason']


class PurchaseReturnItemForm(forms.ModelForm):

    class Meta:
        model = PurchaseReturnItem
        fields = ['purchase_item', 'quantity', 'return_price']

    def __init__(self, *args, purchase=None, **kwargs):
        super().__init__(*args, **kwargs)

        if purchase:
            self.fields['purchase_item'].queryset = (
                PurchaseItem.objects.filter(purchase=purchase)
            )

class SupplierPaymentForm(forms.ModelForm):

    class Meta:
        model = SupplierPayment
        fields = [
            'amount',
            'payment_method',
            'notes'
        ]