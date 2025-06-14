from django import forms
from .models import Order, Delivery, DeliveryItem
from django.core.exceptions import ValidationError
from datetime import date

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['date', 'client', 'status']

class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            current_status = instance.status
            if current_status == 'new':
                # Если статус "Новый", можно выбрать только "В работе" или "Отменен"
                self.fields['status'].choices = [
                    ('new', 'Новый'),
                    ('in_progress', 'В работе'),
                    ('cancelled', 'Отменен')
                ]
            elif current_status == 'in_progress':
                # Если статус "В работе", можно выбрать только "Выполнен" или "Отменен"
                self.fields['status'].choices = [
                    ('in_progress', 'В работе'),
                    ('completed', 'Выполнен'),
                    ('cancelled', 'Отменен')
                ]
            elif current_status == 'cancelled':
                # Если статус "Отменен", нельзя менять
                self.fields['status'].widget.attrs['disabled'] = True
            elif current_status == 'completed':
                # Если статус "Выполнен", нельзя менять
                self.fields['status'].widget.attrs['disabled'] = True 

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status'] 

class DeliveryAdminForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = []  # Пустой список, так как все поля заполняются автоматически

class DeliveryItemForm(forms.ModelForm):
    class Meta:
        model = DeliveryItem
        fields = ['product', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '1'})
        } 