from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import LoyaltySettings, Member
from cart.cart import Cart
from marketing.models import Coupon, PromotionRule
from products.models import ProductVariant

from .models import Order, OrderItem
from .payment import available_payment_methods, is_payment_method_available


def _resolve_promotions(subtotal):
    discount_rule = (
        PromotionRule.objects
        .filter(is_active=True, reward_type=PromotionRule.RewardType.DISCOUNT, min_spend__lte=subtotal)
        .order_by('-min_spend')
        .first()
    )
    gift_rule = (
        PromotionRule.objects
        .filter(is_active=True, reward_type=PromotionRule.RewardType.FREE_GIFT, min_spend__lte=subtotal)
        .order_by('-min_spend')
        .first()
    )
    return discount_rule, gift_rule


def _resolve_coupon(code, member, subtotal):
    code = (code or '').strip()
    if not code:
        return None, Decimal('0'), None

    try:
        coupon = Coupon.objects.get(code__iexact=code)
    except Coupon.DoesNotExist:
        return None, Decimal('0'), '優惠碼不存在'

    if not coupon.is_valid_now():
        return None, Decimal('0'), '優惠碼已失效或已達使用上限'
    if subtotal < coupon.min_spend:
        return None, Decimal('0'), f'需滿 NT$ {coupon.min_spend:.0f} 才能使用此優惠碼'
    if coupon.first_purchase_only and Order.objects.filter(member=member).exists():
        return None, Decimal('0'), '此優惠碼僅限首次購買使用'

    return coupon, coupon.calculate_discount(subtotal), None


def _resolve_points(use_points, member, remaining, loyalty):
    if not use_points or member.points <= 0 or remaining <= 0:
        return 0, Decimal('0')

    max_by_balance = member.points
    max_by_amount = int(remaining * loyalty.points_redeem_rate)
    points_to_use = min(max_by_balance, max_by_amount)
    if points_to_use <= 0:
        return 0, Decimal('0')

    discount = (Decimal(points_to_use) / loyalty.points_redeem_rate).quantize(Decimal('0.01'))
    discount = min(discount, remaining)
    return points_to_use, discount


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
        messages.success(request, f'優惠碼 {coupon.code} 套用成功，折抵 NT$ {coupon_discount:.0f}')

    remaining = max(subtotal - promotion_discount - coupon_discount, Decimal('0'))
    points_to_use, points_discount = _resolve_points(use_points, member, remaining, loyalty)
    total_amount = max(remaining - points_discount, Decimal('0'))

    if request.method == 'POST' and action == 'place_order':
        recipient_name = request.POST.get('recipient_name', '').strip()
        recipient_phone = request.POST.get('recipient_phone', '').strip()
        shipping_address = request.POST.get('shipping_address', '').strip()
        payment_method = request.POST.get('payment_method', '')
        shipping_method = request.POST.get('shipping_method', '')
        store_name = request.POST.get('store_name', '').strip()

        if not recipient_name:
            errors.append('請輸入收件人姓名')
        if not recipient_phone:
            errors.append('請輸入收件人電話')
        if not shipping_address:
            errors.append('請輸入收件地址')
        if not is_payment_method_available(payment_method):
            errors.append('目前僅開放貨到付款')
        if shipping_method not in Order.ShippingMethod.values:
            errors.append('請選擇物流方式')
        if shipping_method == Order.ShippingMethod.CONVENIENCE_STORE and not store_name:
            errors.append('請填寫超商門市名稱')

        for item in cart:
            if item['quantity'] > item['variant'].stock:
                errors.append(
                    f"{item['variant'].product.name}（{item['variant'].get_size_display()} / "
                    f"{item['variant'].color}）庫存不足，請回購物車調整數量"
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
                    shipping_method=shipping_method,
                    recipient_name=recipient_name,
                    recipient_phone=recipient_phone,
                    shipping_address=shipping_address,
                    store_name=store_name if shipping_method == Order.ShippingMethod.CONVENIENCE_STORE else '',
                    subtotal_amount=subtotal,
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

    context = {
        'cart': cart,
        'errors': errors,
        'form_data': form_data,
        'payment_methods': available_payment_methods(),
        'selected_payment_method': form_data.get('payment_method', Order.PaymentMethod.COD),
        'shipping_methods': Order.ShippingMethod.choices,
        'subtotal': subtotal,
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
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def checkout_done(request, order_id):
    order = get_object_or_404(Order, pk=order_id, member=request.user)
    return render(request, 'orders/checkout_done.html', {
        'order': order,
        'bank_transfer': {
            'bank_name': settings.BANK_TRANSFER_BANK_NAME,
            'bank_code': settings.BANK_TRANSFER_BANK_CODE,
            'account_number': settings.BANK_TRANSFER_ACCOUNT_NUMBER,
        },
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(member=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, member=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
@require_POST
def order_request_return(request, pk):
    order = get_object_or_404(Order, pk=pk, member=request.user)
    if order.status != Order.Status.COMPLETED:
        messages.warning(request, '只有已完成的訂單可以申請退貨')
        return redirect('orders:order_detail', pk=order.pk)

    reason = request.POST.get('reason', '').strip()
    if not reason:
        messages.warning(request, '請填寫退貨原因')
        return redirect('orders:order_detail', pk=order.pk)

    order.status = Order.Status.RETURNING
    order.return_reason = reason
    order.save(update_fields=['status', 'return_reason', 'updated_at'])
    messages.success(request, '退貨申請已送出，我們會盡快為您處理')
    return redirect('orders:order_detail', pk=order.pk)


@staff_member_required
def sales_dashboard(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)

    monthly_orders = Order.objects.filter(created_at__date__gte=month_start)
    monthly_revenue = monthly_orders.filter(
        status=Order.Status.COMPLETED
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    monthly_order_count = monthly_orders.count()

    top_products = (
        OrderItem.objects
        .exclude(order__status=Order.Status.RETURNED)
        .values('product_variant__product__name')
        .annotate(total_qty=Sum('quantity'))
        .order_by('-total_qty')[:10]
    )

    trend = []
    max_amount = Decimal('0')
    for days_ago in range(6, -1, -1):
        day = today - timedelta(days=days_ago)
        day_total = Order.objects.filter(
            status=Order.Status.COMPLETED, created_at__date=day
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        trend.append({'date': day, 'total': day_total})
        max_amount = max(max_amount, day_total)

    for row in trend:
        row['bar_percent'] = int((row['total'] / max_amount) * 100) if max_amount else 0

    context = {
        'monthly_revenue': monthly_revenue,
        'monthly_order_count': monthly_order_count,
        'top_products': top_products,
        'trend': trend,
        'month_label': f'{today.year}年{today.month}月',
    }
    return render(request, 'admin/dashboard.html', context)
