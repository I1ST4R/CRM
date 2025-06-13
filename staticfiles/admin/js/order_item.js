(function() {
    'use strict';

    
    function updateItemTotal(row) {
        var productSelect = django.jQuery(row).find('select[id$="-product"]');
        var productId = productSelect.val();
        var quantityInput = django.jQuery(row).find('input[id$="-quantity"]');
        var quantity = parseInt(quantityInput.val()) || 0;
        
        if (productId) {
            django.jQuery.get(`/core/api/product/${productId}/price/`, function(data) {
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
                totalField.text(total.toFixed(2) + ' ₽');
                
                // Обновляем общую сумму заказа
                updateOrderTotal();
            });
        } else {
            quantityInput.val(1); // Устанавливаем минимальное значение
            django.jQuery(row).find('.field-get_item_total').text('0.00 ₽');
            updateOrderTotal();
        }
    }

    function updateOrderTotal() {
        var total = 0;
        django.jQuery('.inline-related').each(function() {
            var totalText = django.jQuery(this).find('.field-get_item_total').text();
            if (totalText) {
                total += parseFloat(totalText.replace(' ₽', '')) || 0;
            }
        });
        django.jQuery('#id_total_amount').val(total.toFixed(2));
    }

    // Ждем загрузки jQuery
    function waitForJQuery(callback) {
        if (window.django && window.django.jQuery) {
            callback(window.django.jQuery);
        } else {
            setTimeout(function() {
                waitForJQuery(callback);
            }, 50);
        }
    }

    waitForJQuery(function($) {
        // Функция для получения списка уже выбранных товаров
        function getSelectedProducts() {
            const selectedProducts = [];
            $('select[id$="-product"]').each(function() {
                const productId = $(this).val();
                if (productId) {
                    selectedProducts.push(productId);
                }
            });
            return selectedProducts;
        }

        // Функция для обновления доступных опций в селектах товаров
        function updateProductOptions() {
            const selectedProducts = getSelectedProducts();
            
            $('select[id$="-product"]').each(function() {
                const currentSelect = $(this);
                const currentValue = currentSelect.val();
                
                // Блокируем все опции
                currentSelect.find('option').each(function() {
                    const option = $(this);
                    const optionValue = option.val();
                    
                    if (optionValue === '') {
                        // Пустая опция всегда доступна
                        option.prop('disabled', false);
                    } else if (optionValue === currentValue) {
                        // Текущий выбранный товар всегда доступен
                        option.prop('disabled', false);
                    } else {
                        // Блокируем товар, если он уже выбран в другом поле
                        option.prop('disabled', selectedProducts.includes(optionValue));
                    }
                });
            });
        }

        // Инициализация при загрузке страницы
        $(document).ready(function() {
            updateProductOptions();
        });

        // Обработчик изменения товара
        $(document).on('change', 'select[id$="-product"]', function() {
            var row = $(this).closest('tr');
            var quantityInput = $(row).find('input[id$="-quantity"]');
            quantityInput.val(1); // Устанавливаем минимальное значение
            updateItemTotal(row);
            
            // Обновляем доступные опции во всех селектах
            updateProductOptions();
        });

        // Обработчик изменения количества
        $(document).on('change', 'input[id$="-quantity"]', function() {
            var value = parseInt($(this).val()) || 0;
            var min = parseInt($(this).attr('min')) || 1;
            var max = parseInt($(this).attr('max')) || 1;
            
            // Проверяем минимальное значение
            if (value < min) {
                $(this).val(min);
            }
            // Проверяем максимальное значение
            if (value > max) {
                $(this).val(max);
            }
            
            updateItemTotal($(this).closest('tr'));
        });

        // Обработчик отправки формы
        $('form').on('submit', function(e) {
            var hasItems = false;
            var selectedProducts = getSelectedProducts();
            var uniqueProducts = new Set(selectedProducts);
            
            $('.inline-related').each(function() {
                var productSelect = $(this).find('select[id$="-product"]');
                var quantityInput = $(this).find('input[id$="-quantity"]');
                if (productSelect.val() && parseInt(quantityInput.val()) > 0) {
                    hasItems = true;
                }
            });
            
            if (!hasItems) {
                e.preventDefault();
                alert('Заказ должен содержать хотя бы один товар');
                return false;
            }
            
            if (selectedProducts.length !== uniqueProducts.size) {
                e.preventDefault();
                alert('Ошибка: один и тот же товар не может быть добавлен несколько раз в заказ.');
                return false;
            }
        });

        // Обработчик добавления новой строки
        $(document).on('formset:added', function(event, $row, formsetName) {
            if (formsetName === 'orderitem_set') {
                // Обновляем доступные опции во всех селектах
                updateProductOptions();
            }
        });

        // Обработчик удаления строки
        $(document).on('formset:removed', function(event, $row, formsetName) {
            if (formsetName === 'orderitem_set') {
                // Обновляем доступные опции во всех селектах
                updateProductOptions();
            }
        });

        // Инициализация при загрузке страницы
        $('.inline-related').each(function() {
            var row = $(this);
            var quantityInput = $(row).find('input[id$="-quantity"]');
            quantityInput.val(1); // Устанавливаем минимальное значение
            updateItemTotal(row);
        });
    });
})(); 