from django.urls import path
from . import views

urlpatterns = [
    path('api/product/<int:product_id>/price/', views.get_product_price, name='get_product_price'),
    path('api/customer/<int:customer_id>/orders/', views.get_customer_orders, name='get_customer_orders'),
    path('admin/core/order/report/', views.order_report, name='order_report'),
    path('admin/core/order/report/export/', views.export_order_report, name='export_order_report'),
    path('clients/', views.clients_list, name='clients_list'),
    path('clients/add/', views.client_add, name='client_add'),
    path('clients/<int:client_id>/edit/', views.client_edit, name='client_edit'),
    path('clients/<int:client_id>/delete/', views.client_delete, name='client_delete'),
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('orders/', views.orders_list, name='orders_list'),
    path('orders/add/', views.order_add, name='order_add'),
    path('orders/<int:order_id>/edit/', views.order_edit, name='order_edit'),
    path('orders/<int:order_id>/delete/', views.order_delete, name='order_delete'),
    path('deliveries/', views.deliveries_list, name='deliveries_list'),
    path('deliveries/add/', views.delivery_add, name='delivery_add'),
    path('deliveries/<int:delivery_id>/edit/', views.delivery_edit, name='delivery_edit'),
    path('deliveries/<int:delivery_id>/delete/', views.delivery_delete, name='delivery_delete'),
    path('stock/', views.stock_list, name='stock_list'),
    path('stock/add/', views.stock_add, name='stock_add'),
    path('stock/<int:stock_id>/edit/', views.stock_edit, name='stock_edit'),
    path('stock/<int:stock_id>/delete/', views.stock_delete, name='stock_delete'),
] 