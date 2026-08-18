from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import LoyaltySettings, Member


@admin.register(Member)
class MemberAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone', 'tier', 'points', 'is_staff', 'is_active')
    list_filter = UserAdmin.list_filter + ('tier',)
    fieldsets = UserAdmin.fieldsets + (
        ('會員資訊', {'fields': ('tier', 'points', 'phone')}),
    )


@admin.register(LoyaltySettings)
class LoyaltySettingsAdmin(admin.ModelAdmin):
    list_display = ('silver_threshold', 'gold_threshold', 'points_earn_rate', 'points_redeem_rate')

    def has_add_permission(self, request):
        return not LoyaltySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
