from django.contrib import admin
from ..models import Client

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
    change_form_template = 'admin/core/customer/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['client_id'] = object_id
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Администраторы', 'Менеджеры']).exists() 