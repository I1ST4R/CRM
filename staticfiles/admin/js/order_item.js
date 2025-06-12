(function($) {
    'use strict';
    
    function updateItemTotal(productId, quantity, totalField) {
        if (!productId || !quantity) {
            totalField.text('0.00');
            return;
        }

        $.ajax({
            url: `/core/api/product/${productId}/price/`,
            method: 'GET',
            success: function(response) {
                if (response && response.price) {
                    const price = parseFloat(response.price);
                    const total = price * quantity;
                    totalField.text(total.toFixed(2));
                    updateOrderTotal();
                } else {
                    totalField.text('0.00');
                    updateOrderTotal();
                }
            },
            error: function() {
                totalField.text('0.00');
                updateOrderTotal();
            }
        });
    }

    function updateOrderTotal() {
        let total = 0;
        $('td.field-get_item_total').each(function() {
            const value = parseFloat($(this).text()) || 0;
            total += value;
        });
        $('#id_total_amount').val(total.toFixed(2));
    }

    $(document).ready(function() {
        // Обработчик изменения продукта
        $(document).on('change', 'select[id$="-product"]', function() {
            const productId = $(this).val();
            const row = $(this).closest('tr');
            const quantity = row.find('input[id$="-quantity"]').val() || 0;
            const totalField = row.find('td.field-get_item_total');
            updateItemTotal(productId, quantity, totalField);
        });

        // Обработчик изменения количества
        $(document).on('change', 'input[id$="-quantity"]', function() {
            const quantity = $(this).val() || 0;
            const row = $(this).closest('tr');
            const productId = row.find('select[id$="-product"]').val();
            const totalField = row.find('td.field-get_item_total');
            updateItemTotal(productId, quantity, totalField);
        });

        // Обработчик удаления строки
        $(document).on('click', '.inline-deletelink', function() {
            setTimeout(updateOrderTotal, 100);
        });

        // Инициализация при загрузке страницы
        updateOrderTotal();
    });
})(jQuery); 