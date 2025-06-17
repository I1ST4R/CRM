from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from ..models import StockMovement

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'movement_type', 'date', 'get_source_link')
    list_filter = ('movement_type', 'date', 'product')
    search_fields = ('product__name', 'source_id')
    date_hierarchy = 'date'
    readonly_fields = ('product', 'quantity', 'movement_type', 'date', 'source_type', 'source_id')

    def get_source_link(self, obj):
        if obj.source_type == 'order':
            url = reverse('admin:core_order_change', args=[obj.source_id])
            return format_html('<a href="{}">Заказ #{}</a>', url, obj.source_id)
        elif obj.source_type == 'delivery':
            url = reverse('admin:core_delivery_change', args=[obj.source_id])
            return format_html('<a href="{}">Поставка #{}</a>', url, obj.source_id)
        return '-'
    get_source_link.short_description = 'Источник'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False 