from django.urls import path
from . import views


urlpatterns = [
    path('add/', views.add_product, name='add_product'),
    path('list/', views.product_list, name='product_list'),
    path('update/<int:id>/', views.update_product, name='update_product'),
path('delete/<int:id>/', views.delete_product, name='delete_product'),path('stock-history/', views.stock_history, name='stock_history'),]