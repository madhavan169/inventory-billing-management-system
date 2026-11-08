from django.urls import path
from . import views

urlpatterns = [

    path('add/', views.add_supplier, name='add_supplier'),
path('list/', views.supplier_list, name='supplier_list'),
path('update/<int:id>/', views.update_supplier, name='update_supplier'),
path('delete/<int:id>/', views.delete_supplier, name='delete_supplier'),
]