from django.contrib.auth.models import AbstractUser
from django.db import models


class Member(AbstractUser):
    """自訂會員，延伸 Django 內建 User，加上會員等級與點數。"""

    class Tier(models.TextChoices):
        BRONZE = 'bronze', '銅級會員'
        SILVER = 'silver', '銀級會員'
        GOLD = 'gold', '金級會員'
        PLATINUM = 'platinum', '白金會員'

    tier = models.CharField(
        max_length=20,
        choices=Tier.choices,
        default=Tier.BRONZE,
        verbose_name='會員等級',
    )
    points = models.PositiveIntegerField(default=0, verbose_name='點數')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手機號碼')

    def __str__(self):
        return self.username


TIER_RANK = {
    Member.Tier.BRONZE: 0,
    Member.Tier.SILVER: 1,
    Member.Tier.GOLD: 2,
    Member.Tier.PLATINUM: 3,
}


class LoyaltySettings(models.Model):
    """會員等級與點數規則設定（全站只有一筆，後台可調整）。"""

    silver_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=3000,
        verbose_name='升級銀卡門檻', help_text='累計已完成訂單金額達到此門檻自動升級為銀卡會員',
    )
    gold_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=10000,
        verbose_name='升級金卡門檻', help_text='累計已完成訂單金額達到此門檻自動升級為金卡會員',
    )
    points_earn_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=1,
        verbose_name='消費 1 元可得點數', help_text='訂單完成時依「實付金額 x 此比例」無條件捨去計算獲得點數',
    )
    points_redeem_rate = models.DecimalField(
        max_digits=6, decimal_places=2, default=10,
        verbose_name='折抵 1 元所需點數', help_text='例如設 10，代表 10 點可折抵 NT$1（即 100 點折 NT$10）',
    )

    class Meta:
        verbose_name = '會員等級與點數設定'
        verbose_name_plural = '會員等級與點數設定'

    def __str__(self):
        return '會員等級與點數設定'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
