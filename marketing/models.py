from decimal import Decimal

from django.db import models
from django.utils import timezone

from accounts.models import Member


class Coupon(models.Model):
    """優惠券 / 折扣碼"""

    class DiscountType(models.TextChoices):
        FIXED = 'fixed', '固定金額'
        PERCENTAGE = 'percentage', '百分比'

    code = models.CharField(max_length=30, unique=True, verbose_name='優惠碼')
    discount_type = models.CharField(
        max_length=20, choices=DiscountType.choices, default=DiscountType.FIXED, verbose_name='折扣類型'
    )
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name='折扣數值',
        help_text='固定金額請填元數（例如 100）；百分比請填 0-100（例如 10 代表折 10%）',
    )
    min_spend = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name='最低消費金額'
    )
    first_purchase_only = models.BooleanField(default=False, verbose_name='限首次購買')
    valid_from = models.DateTimeField(default=timezone.now, verbose_name='生效時間')
    valid_until = models.DateTimeField(verbose_name='到期時間')
    usage_limit = models.PositiveIntegerField(
        null=True, blank=True, verbose_name='使用次數上限', help_text='留空代表不限制次數'
    )
    used_count = models.PositiveIntegerField(default=0, verbose_name='已使用次數')
    is_active = models.BooleanField(default=True, verbose_name='啟用中')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '優惠券'
        verbose_name_plural = '優惠券'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def is_valid_now(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.valid_from <= now <= self.valid_until):
            return False
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, subtotal):
        if subtotal <= 0:
            return Decimal('0')
        if self.discount_type == self.DiscountType.FIXED:
            discount = self.discount_value
        else:
            discount = (subtotal * self.discount_value / Decimal('100'))
        discount = discount.quantize(Decimal('0.01'))
        return min(discount, subtotal)


class PromotionRule(models.Model):
    """滿額折扣 / 滿額贈品規則"""

    class RewardType(models.TextChoices):
        DISCOUNT = 'discount', '折抵金額'
        FREE_GIFT = 'free_gift', '贈送商品'

    name = models.CharField(max_length=100, verbose_name='活動名稱')
    min_spend = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='門檻金額')
    reward_type = models.CharField(
        max_length=20, choices=RewardType.choices, default=RewardType.DISCOUNT, verbose_name='優惠類型'
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name='折抵金額', help_text='優惠類型為「折抵金額」時填寫',
    )
    free_gift_product = models.ForeignKey(
        'products.Product', null=True, blank=True, on_delete=models.SET_NULL,
        related_name='promotion_rules', verbose_name='贈品',
        help_text='優惠類型為「贈送商品」時選擇，出貨時請記得附上贈品',
    )
    is_active = models.BooleanField(default=True, verbose_name='啟用中')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '滿額活動'
        verbose_name_plural = '滿額活動'
        ordering = ['min_spend']

    def __str__(self):
        return self.name


class Announcement(models.Model):
    """會員專屬活動通知（後台可選會員等級發送公告，目前發送管道為 Email）"""

    title = models.CharField(max_length=200, verbose_name='標題')
    content = models.TextField(verbose_name='內容')
    target_tier = models.CharField(
        max_length=20, blank=True, choices=Member.Tier.choices, verbose_name='發送對象等級',
        help_text='留空代表發送給所有會員；有選的話只會發給該等級的會員',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='發送時間')
    sent_count = models.PositiveIntegerField(default=0, verbose_name='發送人數')

    class Meta:
        verbose_name = '會員公告'
        verbose_name_plural = '會員公告'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
