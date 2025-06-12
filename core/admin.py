from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.html import format_html, strip_tags
from .models import Client, Product, Order, OrderItem
from .permissions import create_groups
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .forms import OrderAdminForm, OrderEditForm

class CustomUserCreationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('warehouse', 'Кладовщик'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='Роль')

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'get_item_total')
    readonly_fields = ('get_item_total',)

    def get_item_total(self, obj):
        if obj.pk and obj.product:
            return obj.product.price * obj.quantity
        return ''
    get_item_total.short_description = 'Сумма'

class ReadOnlyOrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    max_num = 0
    fields = ('product', 'quantity', 'get_item_total')
    readonly_fields = ('product', 'quantity', 'get_item_total')

    def get_item_total(self, obj):
        if obj.pk and obj.product:
            return obj.product.price * obj.quantity
        return ''
    get_item_total.short_description = 'Сумма'

    def has_add_permission(self, request, obj=None):
        return False

class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_groups')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'Группы'

    def get_fieldsets(self, request, obj=None):
        if not obj:  # Если это форма создания
            return (
                (None, {'fields': ('username', 'password1', 'password2')}),
                ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
                ('Роль', {'fields': ('role',)}),
            )
        return super().get_fieldsets(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового пользователя
            obj.is_staff = True  # Разрешаем доступ к админке
        super().save_model(request, obj, form, change)
        # Создаем группы при первом сохранении
        create_groups()
        
        if not change:  # Если это создание нового пользователя
            role = form.cleaned_data.get('role')
            if role == 'admin':
                obj.groups.add(Group.objects.get(name='Администраторы'))
            elif role == 'manager':
                obj.groups.add(Group.objects.get(name='Менеджеры'))
            elif role == 'warehouse':
                obj.groups.add(Group.objects.get(name='Кладовщики'))

# Перерегистрируем UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone', 'address')
    list_filter = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Дополнительно', {
            'fields': ('address', 'notes'),
            'classes': ('collapse',)
        }),
    )

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной')
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock < 0:
            raise forms.ValidationError('Количество товара не может быть отрицательным')
        return stock

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            # Удаляем все HTML теги
            description = strip_tags(description)
        return description

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'price', 'stock', 'created_at', 'get_description')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'price', 'stock')
        }),
        ('Описание', {
            'fields': ('description',),
            'description': 'Подробное описание товара.'
        }),
    )

    def get_description(self, obj):
        if obj.description:
            # Обрезаем описание до 100 символов и добавляем многоточие
            short_desc = obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
            return format_html('<span title="{}">{}</span>', obj.description, short_desc)
        return '-'
    get_description.short_description = 'Описание'

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Администраторы', 'Кладовщики']).exists()

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean_date(self):
        order_date = self.cleaned_data['date']
        today = date.today()
        if order_date < today:
            raise ValidationError('Дата заказа не может быть в прошлом')
        return order_date

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ('id', 'date', 'client', 'status', 'get_total_amount', 'created_at')
    list_filter = ('status', 'date', 'client')
    search_fields = ('id', 'client__name')
    date_hierarchy = 'date'
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'date', 'client', 'get_total_amount', 'created_by')
    
    def get_total_amount(self, obj):
        return obj.total_amount
    get_total_amount.short_description = 'Итоговая сумма'
    
    def get_fieldsets(self, request, obj=None):
        if obj:  # Если это просмотр/редактирование существующего объекта
            return (
                ('Основная информация', {
                    'fields': ('date', 'client', 'status', 'get_total_amount', 'created_by')
                }),
            )
        return (
            ('Основная информация', {
                'fields': ('date', 'client', 'status')
            }),
        )

    def get_readonly_fields(self, request, obj=None):
        if not obj:  # Если это создание нового объекта
            return ('status',)
        return ('date', 'client', 'get_total_amount', 'created_by')

    def get_form(self, request, obj=None, **kwargs):
        if obj:  # Если это редактирование существующего объекта
            return OrderEditForm
        return super().get_form(request, obj, **kwargs)

    def has_change_permission(self, request, obj=None):
        if obj and obj.status in ['cancelled', 'completed']:
            return False
        return super().has_change_permission(request, obj)

    def get_inline_instances(self, request, obj=None):
        if obj:  # Если это редактирование существующего объекта
            return [ReadOnlyOrderItemInline(self.model, self.admin_site)]
        return super().get_inline_instances(request, obj)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['js_files'] = ['admin/js/order_item.js']
        return super().changeform_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['js_files'] = ['admin/js/order_item.js']
        return super().add_view(request, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового объекта
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        order = form.instance
        # Пересчитываем сумму заказа
        total = sum(
            item.price * item.quantity for item in order.items.all()
        )
        if order.total_amount != total:
            order.total_amount = total
            order.save(update_fields=['total_amount'])
