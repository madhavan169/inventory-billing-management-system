from django.urls import path
from . import views

urlpatterns = [

    path('create/', views.create_bill, name='create_bill'),

    path(
        'add-item/<int:bill_id>/',
        views.add_bill_item,
        name='add_bill_item'
    ),

    path(
        'history/',
        views.bill_history,
        name='bill_history'
    ),

    path(
        'details/<int:bill_id>/',
        views.bill_details,
        name='bill_details'
    ),
    path(
    'update-payment/<int:bill_id>/',
    views.update_payment_status,
    name='update_bill_payment_status'
),
    path(
    'remove-item/<int:bill_id>/<int:item_id>/',
    views.remove_bill_item,
    name='remove_bill_item'
),path(
    '',
    views.billing_dashboard,
    name='billing_dashboard'
),

]