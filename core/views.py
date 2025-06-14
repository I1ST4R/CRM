from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Product, Order, Client
import json
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.db.models import F, Count, Sum
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime

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

@staff_member_required
def order_report(request):
    # Получаем параметры фильтрации
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    client_id = request.GET.get('client')

    # Базовый queryset
    orders = Order.objects.all()

    # Применяем фильтры
    if date_from:
        orders = orders.filter(date__gte=date_from)
    if date_to:
        orders = orders.filter(date__lte=date_to)
    if client_id:
        orders = orders.filter(client_id=client_id)

    # Получаем статистику по статусам
    total_orders = orders.count()
    status_stats = []
    
    if total_orders > 0:
        for status, status_display in Order.STATUS_CHOICES:
            count = orders.filter(status=status).count()
            percent = round((count / total_orders) * 100, 1)
            status_stats.append((status_display, count, percent))

    # Получаем общую сумму
    total_amount = orders.aggregate(total=Sum('total_amount'))['total'] or 0

    # Получаем список всех клиентов для выпадающего списка
    clients = Client.objects.all().order_by('name')

    context = {
        'orders': orders.order_by('-date'),
        'status_stats': status_stats,
        'total_amount': total_amount,
        'clients': clients,
        'date_from': date_from,
        'date_to': date_to,
        'selected_client': client_id,
    }

    return render(request, 'admin/core/order/report.html', context)
