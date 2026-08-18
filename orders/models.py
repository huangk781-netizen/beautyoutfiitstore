from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import F, Sum

from products.models import ProductVariant


class Order(models.Model):
    """訂單主檔"""

    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = 'bank_transfer', 'ATM/銀行匯款'
        COD = 'cod', '貨到付款'

    class ShippingMethod(models.TextChoices):
        HOME_DELIVERY = 'home_delivery', '宅配到家'
        CONVENIENCE_STORE = 'convenience_store', '超商取貨'

    class Status(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', '待付款'
        PAID = 'paid', '已付款'
        PREPARING = 'preparing', '備貨中'
        SHIPPED = 'shipped', '已出貨'
        COMPLETED = 'completed', '已完成'
        RETURNING = 'returning', '退貨中'
        RETURNED = 'returned', '已退貨'

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders', verbose_name='會員'
    )
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, verbose_name='付款方式'
    )
    shipping_method = models.CharField(
        max_length=20, choices=ShippingMethod.choices, default=ShippingMethod.HOME_DELIVERY, verbose_name='物流方式'
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT, verbose_name='訂單狀態'
    )

    recipient_name = models.CharField(max_length=100, verbose_name='收件人姓名')
    recipient_phone = models.CharField(max_length=20, verbose_name='收件人電話')
    shipping_address = models.CharField(max_length=255, verbose_name='收件地址')
    store_name = models.CharField(max_length=100, blank=True, verbose_name='超商門市名稱')

    subtotal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='小計')

    coupon = models.ForeignKey(
        'marketing.Coupon', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='orders', verbose_name='使用的優惠券',
    )
    coupon_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='優惠券折扣'
    )

    promotion = models.ForeignKey(
        'marketing.PromotionRule', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='orders', verbose_name='套用的滿額活動',
    )
    promotion_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='滿額折扣'
    )
    gift_description = models.CharField(
        max_length=200, blank=True, verbose_name='贈品', help_text='出貨時記得附上此贈品'
    )

    points_used = models.PositiveIntegerField(default=0, verbose_name='使用點數')
    points_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='點數折抵金額'
    )
    points_earned = models.PositiveIntegerField(default=0, verbose_name='本單獲得點數')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='訂單總金額')
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name='託運單號')
    return_reason = models.TextField(blank=True, verbose_name='退貨原因')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '訂單'
        verbose_name_plural = '訂單'
        ordering = ['-created_at']

    def __str__(self):
        return f'訂單 #{self.pk} - {self.member.username}'

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = Order.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        super().save(*args, **kwargs)

        if previous_status != self.Status.COMPLETED and self.status == self.Status.COMPLETED:
            self._apply_loyalty_rewards()

        if previous_status != self.Status.SHIPPED and self.status == self.Status.SHIPPED:
            self._send_shipped_email()

    def _send_shipped_email(self):
        from django.core.mail import send_mail

        member = self.member
        if not member.email:
            return

        subject = f'【beauty_outfits_store】您的訂單 #{self.pk} 已出貨'
        message = (
            f'{member.username} 您好，\n\n'
            f'您的訂單 #{self.pk} 已出貨，出貨明細如下：\n\n'
            f'託運單號：{self.tracking_number or "（尚未提供）"}\n'
            f'物流方式：{self.get_shipping_method_display()}\n'
            f'收件人：{self.recipient_name}（{self.recipient_phone}）\n'
            f'收件地址：{self.shipping_address}\n\n'
            f'感謝您在 beauty_outfits_store 購物！'
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=None,
            recipient_list=[member.email],
            fail_silently=True,
        )

    def _apply_loyalty_rewards(self):
        from accounts.models import TIER_RANK, LoyaltySettings, Member

        loyalty = LoyaltySettings.get_solo()
        member = self.member

        earned_points = int(self.total_amount * loyalty.points_earn_rate)
        if earned_points and not self.points_earned:
            Order.objects.filter(pk=self.pk).update(points_earned=earned_points)

        total_spent = Order.objects.filter(
            member=member, status=Order.Status.COMPLETED
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        if total_spent >= loyalty.gold_threshold:
            computed_tier = Member.Tier.GOLD
        elif total_spent >= loyalty.silver_threshold:
            computed_tier = Member.Tier.SILVER
        else:
            computed_tier = Member.Tier.BRONZE

        update_fields = {'points': F('points') + earned_points}
        if TIER_RANK[computed_tier] > TIER_RANK[member.tier]:
            update_fields['tier'] = computed_tier

        Member.objects.filter(pk=member.pk).update(**update_fields)


class OrderItem(models.Model):
    """訂單明細"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items', verbose_name='訂單'
    )
    product_variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name='order_items', verbose_name='商品規格'
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name='數量')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='單價')

    class Meta:
        verbose_name = '訂單明細'
        verbose_name_plural = '訂單明細'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.product_variant} x {self.quantity}'
