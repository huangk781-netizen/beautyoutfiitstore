from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone

from accounts.models import Member

from .models import Announcement, Coupon, PromotionRule


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'discount_value', 'min_spend', 'first_purchase_only',
        'usage_limit', 'used_count', 'is_active', 'valid_from', 'valid_until',
    )
    list_filter = ('discount_type', 'first_purchase_only', 'is_active')
    search_fields = ('code',)
    readonly_fields = ('used_count',)


@admin.register(PromotionRule)
class PromotionRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_spend', 'reward_type', 'discount_amount', 'free_gift_product', 'is_active')
    list_filter = ('reward_type', 'is_active')
    search_fields = ('name',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'target_tier', 'sent_at', 'sent_count', 'created_at')
    list_filter = ('target_tier',)
    search_fields = ('title', 'content')
    readonly_fields = ('sent_at', 'sent_count')
    actions = ['send_announcement']

    @admin.action(description='發送通知給選中的公告（Email，重複執行會再發一次）')
    def send_announcement(self, request, queryset):
        for announcement in queryset:
            members = Member.objects.exclude(email='')
            if announcement.target_tier:
                members = members.filter(tier=announcement.target_tier)

            sent_count = 0
            subject = f'【beauty_outfits_store】{announcement.title}'
            for email in members.values_list('email', flat=True):
                # 逐一寄送（而非一次塞進同一封信的收件人清單），避免會員互相看到彼此的 Email
                send_mail(
                    subject=subject,
                    message=announcement.content,
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=True,
                )
                sent_count += 1

            announcement.sent_at = timezone.now()
            announcement.sent_count = sent_count
            announcement.save(update_fields=['sent_at', 'sent_count'])

        self.message_user(request, f'已發送 {queryset.count()} 則公告')
