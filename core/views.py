from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Product
import json

# Create your views here.

def hello_world(request):
    return HttpResponse("Hello World")

def get_product_price(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        response_data = {'price': str(product.price)}  # Преобразуем Decimal в строку
        print('Sending response:', response_data)  # Отладочная информация
        return JsonResponse(response_data)
    except Product.DoesNotExist:
        print('Product not found:', product_id)  # Отладочная информация
        return JsonResponse({'error': 'Product not found'}, status=404)
    except Exception as e:
        print('Error:', str(e))  # Отладочная информация
        return JsonResponse({'error': str(e)}, status=500)
