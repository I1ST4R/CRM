from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django import forms
from ..permissions import create_groups

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