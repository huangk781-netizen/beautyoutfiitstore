(function () {
  const dataEl = document.getElementById('variants-data');
  if (!dataEl) return;

  const variants = JSON.parse(dataEl.textContent);
  const sizeButtons = Array.from(document.querySelectorAll('.size-btn'));
  const colorButtons = Array.from(document.querySelectorAll('.color-btn'));
  const statusEl = document.getElementById('stock-status');
  const addToCartBtn = document.getElementById('add-to-cart');
  const selectedVariantInput = document.getElementById('selected-variant-id');
  const quantityInput = document.getElementById('selected-quantity');
  const quantityDisplay = document.getElementById('quantity-display');
  const quantityDecreaseBtn = document.getElementById('quantity-decrease');
  const quantityIncreaseBtn = document.getElementById('quantity-increase');

  let selectedSize = null;
  let selectedColor = null;
  let quantity = 1;
  let quantityLocked = true;

  function findVariant(size, color) {
    return variants.find((v) => v.size === size && v.color === color);
  }

  function currentMaxQuantity() {
    const variant = selectedSize && selectedColor ? findVariant(selectedSize, selectedColor) : null;
    return variant ? variant.stock : 1;
  }

  function refreshQuantityButtons() {
    const max = currentMaxQuantity();
    quantityDecreaseBtn.disabled = quantityLocked || quantity <= 1;
    quantityIncreaseBtn.disabled = quantityLocked || quantity >= max;
    [quantityDecreaseBtn, quantityIncreaseBtn].forEach((btn) => {
      btn.classList.toggle('opacity-40', btn.disabled);
      btn.classList.toggle('cursor-not-allowed', btn.disabled);
    });
  }

  function setQuantity(value) {
    const max = Math.max(currentMaxQuantity(), 1);
    quantity = Math.min(Math.max(value, 1), max);
    quantityDisplay.textContent = quantity;
    if (quantityInput) quantityInput.value = quantity;
    refreshQuantityButtons();
  }

  function variantStock(size, color) {
    const variant = findVariant(size, color);
    return variant ? variant.stock : 0;
  }

  function sizeHasStock(size) {
    return variants.some((v) => v.size === size && v.stock > 0);
  }

  function colorHasStock(color) {
    return variants.some((v) => v.color === color && v.stock > 0);
  }

  function setButtonState(btn, disabled, active) {
    btn.disabled = disabled;
    btn.classList.remove(
      'bg-accent', 'text-base', 'border-accent',
      'opacity-40', 'cursor-not-allowed', 'line-through',
      'border-secondary', 'text-neutral', 'hover:border-accent'
    );
    if (disabled) {
      btn.classList.add('opacity-40', 'cursor-not-allowed', 'line-through', 'border-secondary', 'text-neutral');
    } else if (active) {
      btn.classList.add('bg-accent', 'text-base', 'border-accent');
    } else {
      btn.classList.add('border-secondary', 'text-neutral', 'hover:border-accent');
    }
  }

  function updateStatus() {
    if (!selectedSize || !selectedColor) {
      statusEl.textContent = '請選擇尺寸與顏色';
      if (addToCartBtn) addToCartBtn.disabled = true;
      if (selectedVariantInput) selectedVariantInput.value = '';
      quantityLocked = true;
      setQuantity(1);
      return;
    }
    const variant = findVariant(selectedSize, selectedColor);
    const stock = variant ? variant.stock : 0;
    if (variant && stock > 0) {
      statusEl.textContent = `尚有 ${stock} 件`;
      if (addToCartBtn) addToCartBtn.disabled = false;
      if (selectedVariantInput) selectedVariantInput.value = variant.id;
      quantityLocked = false;
      setQuantity(quantity);
    } else {
      statusEl.textContent = '已售完';
      if (addToCartBtn) addToCartBtn.disabled = true;
      if (selectedVariantInput) selectedVariantInput.value = '';
      quantityLocked = true;
      setQuantity(1);
    }
  }

  function refresh() {
    sizeButtons.forEach((btn) => {
      const size = btn.dataset.size;
      const disabled = selectedColor
        ? variantStock(size, selectedColor) <= 0
        : !sizeHasStock(size);
      setButtonState(btn, disabled, size === selectedSize);
    });

    colorButtons.forEach((btn) => {
      const color = btn.dataset.color;
      const disabled = selectedSize
        ? variantStock(selectedSize, color) <= 0
        : !colorHasStock(color);
      setButtonState(btn, disabled, color === selectedColor);
    });

    updateStatus();
  }

  sizeButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      if (btn.disabled) return;
      selectedSize = btn.dataset.size;
      refresh();
    });
  });

  colorButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      if (btn.disabled) return;
      selectedColor = btn.dataset.color;
      refresh();
    });
  });

  quantityDecreaseBtn.addEventListener('click', () => {
    if (quantityDecreaseBtn.disabled) return;
    setQuantity(quantity - 1);
  });

  quantityIncreaseBtn.addEventListener('click', () => {
    if (quantityIncreaseBtn.disabled) return;
    setQuantity(quantity + 1);
  });

  refresh();
})();
