from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Product, Order, Client
import json
from django.views.decorators.http import require_http_methods
from django.core.serializers import serialize
from django.db.models import F, Count, Sum
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from django.utils import timezone

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

@staff_member_required
def export_order_report(request):
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

    # Создаем новый Excel файл
    wb = Workbook()
    ws = wb.active
    ws.title = "Отчет по заказам"

    # Стили для заголовков
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="417690", end_color="417690", fill_type="solid")
    header_alignment = Alignment(horizontal='center', vertical='center')

    # Заголовки
    headers = ['Номер заказа', 'Дата', 'Клиент', 'Статус', 'Сумма']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col)
        cell.value = header
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    # Данные
    for row, order in enumerate(orders.order_by('-date'), 2):
        ws.cell(row=row, column=1, value=f"Заказ #{order.id}")
        ws.cell(row=row, column=2, value=order.date.strftime('%d.%m.%Y'))
        ws.cell(row=row, column=3, value=order.client.name)
        ws.cell(row=row, column=4, value=order.get_status_display())
        ws.cell(row=row, column=5, value=order.total_amount)

    # Добавляем статистику
    ws.append([])  # Пустая строка
    ws.append(['Статистика по статусам'])
    ws.append(['Статус', 'Количество', 'Процент'])

    total_orders = orders.count()
    if total_orders > 0:
        for status, status_display in Order.STATUS_CHOICES:
            count = orders.filter(status=status).count()
            percent = round((count / total_orders) * 100, 1)
            ws.append([status_display, count, f"{percent}%"])

    # Общая сумма
    total_amount = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    ws.append([])
    ws.append(['Общая сумма заказов:', total_amount])

    # Настройка ширины столбцов
    for col in ws.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column].width = adjusted_width

    # Создаем ответ
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=order_report_{timezone.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    wb.save(response)
    return response
