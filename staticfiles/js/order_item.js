django.jQuery(function() {
    'use strict';
    
    console.log('=== DEBUG INFO START ===');
    console.log('jQuery version:', django.jQuery.fn.jquery);
    console.log('All forms on page:', django.jQuery('form').length);
    console.log('Form IDs:', django.jQuery('form').map(function() { return this.id; }).get());
    console.log('All product selects:', django.jQuery('select[id$="-product"]').length);
    console.log('Product select IDs:', django.jQuery('select[id$="-product"]').map(function() { return this.id; }).get());
    console.log('All inline-related elements:', django.jQuery('.inline-related').length);
    console.log('Total amount field exists:', django.jQuery('#id_total_amount').length);
    console.log('=== DEBUG INFO END ===');
    
    function updateItemTotal(row) {
        console.log('updateItemTotal called for row:', row);
        var productSelect = django.jQuery(row).find('select[id$="-product"]');
        var productId = productSelect.val();
        var quantityInput = django.jQuery(row).find('input[id$="-quantity"]');
        var quantity = parseInt(quantityInput.val()) || 0;
        
        console.log('Product ID:', productId);
        console.log('Quantity:', quantity);
        
        if (productId) {
            console.log('Fetching price for product:', productId);
            django.jQuery.get(`/core/api/product/${productId}/price/`, function(data) {
                console.log('Price data received:', data);
                // Устанавливаем минимальное и максимальное значение
                quantityInput.attr('min', 1);
                quantityInput.attr('max', data.stock);
                
                // Проверяем текущее значение
                if (quantity < 1) {
                    quantityInput.val(1);
                    quantity = 1;
                } else if (quantity > data.stock) {
                    quantityInput.val(data.stock);
                    quantity = data.stock;
                }
                
                // Обновляем итоговую сумму
                var total = data.price * quantity;
                var totalField = django.jQuery(row).find('.field-get_item_total');
                console.log('Setting total:', total, 'for field:', totalField.length ? 'found' : 'not found');
                totalField.text(total.toFixed(2) + ' ₽');
                
                // Обновляем общую сумму заказа
                updateOrderTotal();
            });
        } else {
            console.log('No product selected, resetting to defaults');
            quantityInput.val(1); // Устанавливаем минимальное значение
            django.jQuery(row).find('.field-get_item_total').text('0.00 ₽');
            updateOrderTotal();
        }
    }

    function updateOrderTotal() {
        console.log('updateOrderTotal called');
        var total = 0;
        django.jQuery('.inline-related').each(function() {
            var totalText = django.jQuery(this).find('.field-get_item_total').text();
            console.log('Found total text:', totalText);
            if (totalText) {
                total += parseFloat(totalText.replace(' ₽', '')) || 0;
            }
        });
        console.log('Setting order total:', total);
        django.jQuery('#id_total_amount').val(total.toFixed(2));
    }

    console.log('Document ready');
    
    // Проверяем, что мы на странице создания заказа
    var isOrderPage = django.jQuery('form').find('select[id$="-product"]').length > 0;
    
    console.log('Form exists:', isOrderPage);
    console.log('product select exists:', django.jQuery('form').find('select[id$="-product"]').length > 0);
    
    if (isOrderPage) {
        console.log('On order creation page');
        
        // Обработчик изменения товара
        django.jQuery(document).on('change', 'select[id$="-product"]', function() {
            console.log('Product changed:', this.value);
            var row = django.jQuery(this).closest('tr');
            var quantityInput = django.jQuery(row).find('input[id$="-quantity"]');
            quantityInput.val(1); // Устанавливаем минимальное значение
            updateItemTotal(row);
        });

        // Обработчик изменения количества
        django.jQuery(document).on('change', 'input[id$="-quantity"]', function() {
            console.log('Quantity changed:', this.value);
            var value = parseInt(django.jQuery(this).val()) || 0;
            var min = parseInt(django.jQuery(this).attr('min')) || 1;
            var max = parseInt(django.jQuery(this).attr('max')) || 1;
            
            // Проверяем минимальное значение
            if (value < min) {
                django.jQuery(this).val(min);
            }
            // Проверяем максимальное значение
            if (value > max) {
                django.jQuery(this).val(max);
            }
            
            console.log('Quantity changed');
            updateItemTotal(django.jQuery(this).closest('tr'));
        });

        // Обработчик отправки формы
        django.jQuery('form').on('submit', function(e) {
            console.log('Form submit attempted');
            var hasItems = false;
            django.jQuery('.inline-related').each(function() {
                var productSelect = django.jQuery(this).find('select[id$="-product"]');
                var quantityInput = django.jQuery(this).find('input[id$="-quantity"]');
                if (productSelect.val() && parseInt(quantityInput.val()) > 0) {
                    hasItems = true;
                }
            });
            
            if (!hasItems) {
                e.preventDefault();
                alert('Заказ должен содержать хотя бы один товар');
                return false;
            }
        });

        // Инициализация при загрузке страницы
        console.log('Initializing inline items');
        django.jQuery('.inline-related').each(function() {
            var row = django.jQuery(this);
            var quantityInput = django.jQuery(row).find('input[id$="-quantity"]');
            console.log('Found inline item:', row.length ? 'yes' : 'no');
            quantityInput.val(1); // Устанавливаем минимальное значение
            updateItemTotal(row);
        });
    } else {
        console.log('Not on order creation page');
    }
}); 