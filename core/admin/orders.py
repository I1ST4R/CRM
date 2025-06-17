from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from ..models import Order, OrderItem, StockMovement
from ..forms import OrderAdminForm, OrderEditForm, OrderStatusForm

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity', 'get_item_total')
    readonly_fields = ('get_item_total',)

    def get_item_total(self, obj):
        if obj.id:  # Если это существующий объект
            return f"{obj.get_total():.2f} ₽"
        return '0.00 ₽'  # Для новых объектов
    get_item_total.short_description = 'Итого'

    class Media:
        js = ('admin/js/order_item.js',)

class ReadOnlyOrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    max_num = 0
    fields = ('product', 'quantity', 'get_item_total')
    readonly_fields = ('product', 'quantity', 'get_item_total')

    def get_item_total(self, obj):
        if obj.id:  # Если это существующий объект
            return f"{obj.get_total():.2f} ₽"
        return '0.00 ₽'  # Для новых объектов
    get_item_total.short_description = 'Итого'

    def has_add_permission(self, request, obj=None):
        return False

    class Media:
        js = ()  # Отключаем JavaScript для просмотра заказа

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = ('id', 'date', 'client', 'status', 'get_total_amount', 'created_by', 'created_at')
    list_filter = ('status', 'date', 'client', 'created_by')
    search_fields = ('id', 'client__name', 'created_by__username')
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
            if request.POST.get('_save') == 'Сохранить':  # Если это изменение статуса
                return OrderStatusForm
            return OrderEditForm
        return super().get_form(request, obj, **kwargs)
    
    def has_change_permission(self, request, obj=None):
        if obj and obj.status in ['cancelled', 'completed']:
            return False
        return super().has_change_permission(request, obj)

    def get_inline_instances(self, request, obj=None):
        if obj and obj.status in ['cancelled', 'completed']:
            return [ReadOnlyOrderItemInline(self.model, self.admin_site)]
        return super().get_inline_instances(request, obj)

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового заказа
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'Управление заказами'
        return super().changelist_view(request, extra_context=extra_context)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change:  # Если это создание нового заказа
            # Создаем запись о движении товара
            for formset in formsets:
                for form in formset.forms:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        product = form.cleaned_data['product']
                        quantity = form.cleaned_data['quantity']
                        # Создаем запись о резервировании товара
                        StockMovement.objects.create(
                            product=product,
                            quantity=-quantity,  # Отрицательное количество для резервирования
                            movement_type='reservation',
                            source_type='order',
                            source_id=form.instance.order.id
                        ) 