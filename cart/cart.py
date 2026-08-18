from decimal import Decimal

from products.models import ProductVariant

CART_SESSION_KEY = 'cart'


class Cart:
    """Session 儲存的購物車，key 為 ProductVariant id，value 為數量。"""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def save(self):
        self.session.modified = True

    def get_quantity(self, variant):
        item = self.cart.get(str(variant.id))
        return item['quantity'] if item else 0

    def add(self, variant, quantity=1):
        variant_id = str(variant.id)
        current = self.get_quantity(variant)
        new_quantity = min(current + quantity, variant.stock)
        if new_quantity <= 0:
            return
        self.cart[variant_id] = {'quantity': new_quantity}
        self.save()

    def set_quantity(self, variant, quantity):
        variant_id = str(variant.id)
        quantity = min(quantity, variant.stock)
        if quantity <= 0:
            self.cart.pop(variant_id, None)
        else:
            self.cart[variant_id] = {'quantity': quantity}
        self.save()

    def remove(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def clear(self):
        self.cart.clear()
        self.save()

    def _items(self):
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.select_related('product').filter(id__in=variant_ids)
        variants_map = {str(v.id): v for v in variants}
        items = []
        for variant_id, data in self.cart.items():
            variant = variants_map.get(variant_id)
            if not variant:
                continue
            price = variant.product.price
            quantity = data['quantity']
            items.append({
                'variant': variant,
                'quantity': quantity,
                'price': price,
                'subtotal': price * quantity,
            })
        return items

    def __iter__(self):
        return iter(self._items())

    def __len__(self):
        return sum(data['quantity'] for data in self.cart.values())

    def total_price(self):
        return sum((item['subtotal'] for item in self._items()), Decimal('0'))
