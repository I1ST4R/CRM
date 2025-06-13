from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Client(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес', blank=True)
    notes = models.TextField(verbose_name='Заметки', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    stock = models.IntegerField(default=0, verbose_name='Количество на складе')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    id = models.AutoField(primary_key=True, verbose_name="Номер заказа")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="Клиент")
    date = models.DateField(verbose_name="Дата заказа")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая сумма", editable=False)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name="Менеджер")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return f"Заказ #{self.id}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Товар")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    def clean(self):
        super().clean()
        if self.quantity <= 0:
            raise ValidationError('Количество товара должно быть больше нуля')
        if not self.pk and self.product and self.quantity > self.product.stock:
            raise ValidationError(f'На складе доступно только {self.product.stock} шт. товара')

    def save(self, *args, **kwargs):
        if not self.price and self.product_id:
            self.price = self.product.price
        super().save(*args, **kwargs)

    def get_total(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity} шт."

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"
