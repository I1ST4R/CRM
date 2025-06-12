(function($) {
    'use strict';
    
    function updateItemTotal(row) {
        var productSelect = row.find('select[id$="-product"]');
        var productId = productSelect.val();
        var quantity = parseInt(row.find('input[id$="-quantity"]').val()) || 0;
        
        console.log('Row:', row);
        console.log('Product ID:', productId);
        console.log('Quantity:', quantity);
        
        if (productId) {
            $.get(`/core/api/product/${productId}/price/`, function(data) {
                console.log('Price from API:', data.price);
                var total = data.price * quantity;
                console.log('Total:', total);
                var totalField = row.find('.field-get_item_total');
                console.log('Total field:', totalField);
                totalField.text(total.toFixed(2));
            });
        } else {
            row.find('.field-get_item_total').text('0.00');
        }
    }

    django.jQuery(document).ready(function($) {
        console.log('Document ready');
        // Обработчик изменения товара
        $(document).on('change', 'select[id$="-product"]', function() {
            console.log('Product changed');
            updateItemTotal($(this).closest('tr'));
        });

        // Обработчик изменения количества
        $(document).on('change', 'input[id$="-quantity"]', function() {
            console.log('Quantity changed');
            updateItemTotal($(this).closest('tr'));
        });

        // Инициализация при загрузке страницы
        $('.inline-related').each(function() {
            console.log('Initializing row');
            updateItemTotal($(this));
        });
    });
})(django.jQuery); 