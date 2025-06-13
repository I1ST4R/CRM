from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Product
import json
from django.views.decorators.http import require_http_methods

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
