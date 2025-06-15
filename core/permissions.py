from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Client, Product, Order, Delivery

def create_groups():
    # Создаем группы
    admin_group, _ = Group.objects.get_or_create(name='Администраторы')
    manager_group, _ = Group.objects.get_or_create(name='Менеджеры')
    warehouse_group, _ = Group.objects.get_or_create(name='Кладовщики')

    # Получаем все права для каждой модели
    client_permissions = Permission.objects.filter(content_type__model='client')
    product_permissions = Permission.objects.filter(content_type__model='product')
    order_permissions = Permission.objects.filter(content_type__model='order')
    delivery_permissions = Permission.objects.filter(content_type__model='delivery')

    # Права для менеджеров (клиенты и заказы)
    manager_group.permissions.set(list(client_permissions) + list(order_permissions))

    # Права для кладовщиков (товары и привозы)
    warehouse_group.permissions.set(list(product_permissions) + list(delivery_permissions))

    # Администраторы получают все права автоматически через is_staff=True 