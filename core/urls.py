from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('api/product/<int:product_id>/price/', views.get_product_price, name='get_product_price'),
] 