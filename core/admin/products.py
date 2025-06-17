from django.contrib import admin
from django import forms
from django.utils.html import format_html, strip_tags
from ..models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price']

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price < 0:
            raise forms.ValidationError('Цена не может быть отрицательной')
        return price

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
            'fields': ('name', 'price')
        }),
        ('Описание', {
            'fields': ('description',),
            'description': 'Подробное описание товара.'
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:  # Если это редактирование существующего товара
            return (
                ('Основная информация', {
                    'fields': ('name', 'price', 'stock')
                }),
                ('Описание', {
                    'fields': ('description',),
                    'description': 'Подробное описание товара.'
                }),
            )
        return super().get_fieldsets(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Если это редактирование существующего товара
            return ('stock',)
        return ()

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

    def save_model(self, request, obj, form, change):
        if not change:  # Если это создание нового товара
            obj.stock = 0  # Устанавливаем количество в 0
        super().save_model(request, obj, form, change) 