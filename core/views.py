from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Product, Order, Client
import json
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.db.models import F

# Create your views here.

def hello_world(request):
    return HttpResponse("Hello World")

@require_http_methods(["GET"])
def get_product_price(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            'price': float(product.price),
            'stock': product.stock
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        print('Error:', str(e))  # Отладочная информация
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def get_customer_orders(request, customer_id):
    try:
        client = Client.objects.get(id=customer_id)
        orders = Order.objects.filter(client=client).order_by('-created_at')
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'number': order.id,  # Используем id как номер заказа
                'created_at': order.created_at.strftime('%d.%m.%Y %H:%M'),
                'status': order.get_status_display(),
                'total_amount': float(order.total_amount)
            })
            
        return JsonResponse({
            'orders': orders_data
        })
    except Client.DoesNotExist:
        return JsonResponse({'error': 'Client not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
