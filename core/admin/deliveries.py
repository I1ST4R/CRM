from django.contrib import admin
from ..models import Delivery, DeliveryItem, StockMovement
from ..forms import DeliveryAdminForm

class DeliveryItemInline(admin.TabularInline):
    model = DeliveryItem
    extra = 1
    fields = ('product', 'quantity')

    class Media:
        js = ('/static/admin/js/delivery_item.js',)

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    form = DeliveryAdminForm
    list_display = ('id', 'date', 'created_by', 'created_at')
    list_filter = ('date', 'created_by')
    search_fields = ('id', 'created_by__username')
    date_hierarchy = 'date'
    inlines = [DeliveryItemInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание новой поставки
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if not change:  # Если это создание новой поставки
            # Создаем записи о движении товара
            for formset in formsets:
                for form in formset.forms:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                        product = form.cleaned_data['product']
                        quantity = form.cleaned_data['quantity']
                        # Создаем запись о поступлении товара
                        StockMovement.objects.create(
                            product=product,
                            quantity=quantity,
                            movement_type='delivery',
                            source_type='delivery',
                            source_id=form.instance.delivery.id
                        )
                        # Обновляем количество товара на складе
                        product.stock += quantity
                        product.save() 