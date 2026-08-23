from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect, render

from accounts.models import LoyaltySettings, Member
from cart.cart import Cart
from marketing.models import Coupon
from products.models import ProductVariant

from .models import Order, OrderItem
from .views import _resolve_coupon, _resolve_points, _resolve_promotions


STORE_PICKUP_SHIPPING_FEE = Decimal('60')


@login_required
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')

    member = request.user
    loyalty = LoyaltySettings.get_solo()
    subtotal = cart.total_price()
    errors = []
    form_data = {}
    action = 'place_order'
    coupon_code = ''
    use_points = False

    if request.method == 'POST':
        form_data = request.POST
        action = request.POST.get('checkout_action', 'place_order')
        coupon_code = request.POST.get('coupon_code', '').strip()
        use_points = request.POST.get('use_points') == 'on'

    discount_rule, gift_rule = _resolve_promotions(subtotal)
    promotion_discount = min(discount_rule.discount_amount, subtotal) if discount_rule else Decimal('0')
    coupon, coupon_discount, coupon_warning = _resolve_coupon(coupon_code, member, subtotal)

    if coupon_warning:
        messages.warning(request, coupon_warning)
    elif coupon and action == 'apply_coupon':
        messages.success(request, f'優惠券 {coupon.code} 已套用，折抵 NT$ {coupon_discount:.0f}')

    remaining = max(subtotal - promotion_discount - coupon_discount, Decimal('0'))
    points_to_use, points_discount = _resolve_points(use_points, member, remaining, loyalty)
    item_total = max(remaining - points_discount, Decimal('0'))
    total_amount = item_total + STORE_PICKUP_SHIPPING_FEE

    if request.method == 'POST' and action == 'place_order':
        recipient_name = request.POST.get('recipient_name', '').strip()
        recipient_phone = request.POST.get('recipient_phone', '').strip()
        payment_method = request.POST.get('payment_method', '')
        store_name = request.POST.get('store_name', '').strip()

        if not recipient_name:
            errors.append('請輸入取貨人姓名')
        if not recipient_phone:
            errors.append('請輸入取貨人手機號碼')
        if not store_name:
            errors.append('請輸入超商取貨門市')
        if payment_method not in Order.PaymentMethod.values:
            errors.append('請選擇付款方式')

        for item in cart:
            if item['quantity'] > item['variant'].stock:
                errors.append(
                    f"{item['variant'].product.name}（{item['variant'].get_size_display()} / "
                    f"{item['variant'].color}）庫存不足"
                )

        if not errors:
            gift_description = ''
            if gift_rule:
                gift_description = (
                    f'{gift_rule.name}：{gift_rule.free_gift_product.name}'
                    if gift_rule.free_gift_product else gift_rule.name
                )

            with transaction.atomic():
                order = Order.objects.create(
                    member=member,
                    payment_method=payment_method,
                    shipping_method=Order.ShippingMethod.CONVENIENCE_STORE,
                    recipient_name=recipient_name,
                    recipient_phone=recipient_phone,
                    shipping_address='',
                    store_name=store_name,
                    subtotal_amount=subtotal,
                    shipping_fee=STORE_PICKUP_SHIPPING_FEE,
                    coupon=coupon,
                    coupon_discount_amount=coupon_discount,
                    promotion=discount_rule,
                    promotion_discount_amount=promotion_discount,
                    gift_description=gift_description,
                    points_used=points_to_use,
                    points_discount_amount=points_discount,
                    total_amount=total_amount,
                )
                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        product_variant=item['variant'],
                        quantity=item['quantity'],
                        unit_price=item['price'],
                    )
                    ProductVariant.objects.filter(pk=item['variant'].pk).update(
                        stock=F('stock') - item['quantity']
                    )

                if coupon:
                    Coupon.objects.filter(pk=coupon.pk).update(used_count=F('used_count') + 1)
                if points_to_use:
                    Member.objects.filter(pk=member.pk).update(points=F('points') - points_to_use)

                cart.clear()
            return redirect('orders:checkout_done', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'errors': errors,
        'form_data': form_data,
        'payment_methods': Order.PaymentMethod.choices,
        'subtotal': subtotal,
        'shipping_fee': STORE_PICKUP_SHIPPING_FEE,
        'promotion_rule': discount_rule,
        'promotion_discount': promotion_discount,
        'gift_rule': gift_rule,
        'coupon': coupon,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'member_points': member.points,
        'use_points': use_points,
        'points_to_use': points_to_use,
        'points_discount': points_discount,
        'points_redeem_rate': loyalty.points_redeem_rate,
        'total_amount': total_amount,
    })
