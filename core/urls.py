from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('api/product/<int:product_id>/price/', views.get_product_price, name='get_product_price'),
    path('api/customer/<int:customer_id>/orders/', views.get_customer_orders, name='get_customer_orders'),
    path('admin/core/order/report/', views.order_report, name='order_report'),
    path('admin/core/order/report/export/', views.export_order_report, name='export_order_report'),
] 