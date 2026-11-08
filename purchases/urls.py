from django.urls import path
from . import views

urlpatterns = [
   
    path('create/', views.create_purchase, name='create_purchase'),
    path('add-items/<int:id>/', views.add_purchase_items, name='add_purchase_items'),
    path('list/', views.purchase_list, name='purchase_list'),
    path('details/<int:id>/', views.purchase_details, name='purchase_details'),
    path('report/', views.purchase_report, name='purchase_report'),
    path(
    'update-payment/<int:id>/',
    views.update_payment_status,
    name='update_payment_status'
),path(
    'supplier-report/',
    views.supplier_purchase_report,
    name='supplier_purchase_report'
),path(
    'remove-item/<int:id>/',
    views.remove_purchase_item,
    name='remove_purchase_item'
),path(
    'export/',
    views.export_purchases,
    name='export_purchases'
),path(
    'edit/<int:id>/',
    views.edit_purchase,
    name='edit_purchase'
),path(
    'delete/<int:id>/',
    views.delete_purchase,
    name='delete_purchase'
),path(
    'return/create/',
    views.create_purchase_return,
    name='create_purchase_return'
),

path(
    'return/add-items/<int:id>/',
    views.add_purchase_return_items,
    name='add_purchase_return_items'
),path(
    'return/list/',
    views.purchase_return_list,
    name='purchase_return_list'
),path(
    'return/details/<int:id>/',
    views.purchase_return_details,
    name='purchase_return_details'
),path(
    'return/report/',
    views.purchase_return_report,
    name='purchase_return_report'
),
path(
    'return/export/',
    views.export_purchase_returns,
    name='export_purchase_returns'
),path(
    'return/delete/<int:id>/',
    views.delete_purchase_return,
    name='delete_purchase_return'
),path(
    'return/edit/<int:id>/',
    views.edit_purchase_return,
    name='edit_purchase_return'
),path(
    'return/item/edit/<int:id>/',
    views.edit_purchase_return_item,
    name='edit_purchase_return_item'
),path(
    'return/item/delete/<int:id>/',
    views.delete_purchase_return_item,
    name='delete_purchase_return_item'
),path(
    'payment/add/<int:id>/',
    views.add_supplier_payment,
    name='add_supplier_payment'
),path(
    'payment/list/',
    views.supplier_payment_list,
    name='supplier_payment_list'
),path(
    'payment/export/',
    views.export_supplier_payments,
    name='export_supplier_payments'
),path(
    'payment/edit/<int:id>/',
    views.edit_supplier_payment,
    name='edit_supplier_payment'
),path(
    'payment/delete/<int:id>/',
    views.delete_supplier_payment,
    name='delete_supplier_payment'
),path(
    'payment/report/',
    views.supplier_payment_report,
    name='supplier_payment_report'
),path(
    'payment/receipt/<int:id>/',
    views.supplier_payment_receipt,
    name='supplier_payment_receipt'
),]