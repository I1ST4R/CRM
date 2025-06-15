(function($) {
    console.log('Delivery item JS loaded');

    // Функция для получения списка уже выбранных товаров
    function getSelectedProducts() {
        const selectedProducts = [];
        $('select[id$="-product"]').each(function() {
            const productId = $(this).val();
            if (productId) {
                selectedProducts.push(productId);
            }
        });
        console.log('Selected products:', selectedProducts);
        return selectedProducts;
    }

    // Функция для обновления доступных опций в селектах товаров
    function updateProductOptions() {
        console.log('Updating product options');
        const selectedProducts = getSelectedProducts();
        
        $('select[id$="-product"]').each(function() {
            const currentSelect = $(this);
            const currentValue = currentSelect.val();
            console.log('Current select value:', currentValue);
            
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
                    const isDisabled = selectedProducts.includes(optionValue);
                    option.prop('disabled', isDisabled);
                    console.log('Option', optionValue, 'disabled:', isDisabled);
                }
            });
        });
    }

    // Инициализация при загрузке страницы
    $(document).ready(function() {
        console.log('Document ready');
        updateProductOptions();
    });

    // Обработчик изменения товара
    $(document).on('change', 'select[id$="-product"]', function() {
        console.log('Product changed:', this.value);
        // Обновляем доступные опции во всех селектах
        updateProductOptions();
    });

    // Обработчик отправки формы
    $('form').on('submit', function(e) {
        console.log('Form submit');
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
            alert('Привоз должен содержать хотя бы один товар');
            return false;
        }
        
        if (selectedProducts.length !== uniqueProducts.size) {
            e.preventDefault();
            alert('Ошибка: один и тот же товар не может быть добавлен несколько раз в привоз.');
            return false;
        }
    });

    // Обработчик добавления новой строки
    $(document).on('formset:added', function(event, $row, formsetName) {
        console.log('Formset added:', formsetName);
        if (formsetName === 'deliveryitem_set') {
            // Обновляем доступные опции во всех селектах
            updateProductOptions();
        }
    });

    // Обработчик удаления строки
    $(document).on('formset:removed', function(event, $row, formsetName) {
        console.log('Formset removed:', formsetName);
        if (formsetName === 'deliveryitem_set') {
            // Обновляем доступные опции во всех селектах
            updateProductOptions();
        }
    });
})(django.jQuery); 