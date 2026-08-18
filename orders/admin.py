from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        tracking_number = cleaned_data.get('tracking_number')
        if status == Order.Status.SHIPPED and not tracking_number:
            self.add_error('tracking_number', '訂單狀態改為「已出貨」時，必須填寫託運單號')
        return cleaned_data


STATUS_ADMIN_COLORS = {
    Order.Status.PENDING_PAYMENT: ('#FDEEDB', '#B9670E'),
    Order.Status.PAID: ('#E0F2FE', '#0369A1'),
    Order.Status.PREPARING: ('#F3E8FF', '#7E22CE'),
    Order.Status.SHIPPED: ('#DBEAFE', '#1D4ED8'),
    Order.Status.COMPLETED: ('#DCFCE7', '#15803D'),
    Order.Status.RETURNING: ('#FEE2E2', '#B91C1C'),
    Order.Status.RETURNED: ('#F1F5F9', '#475569'),
}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    form = OrderAdminForm
    list_display = (
        'id', 'member', 'payment_method', 'shipping_method', 'colored_status',
        'tracking_number', 'coupon', 'points_used', 'points_earned', 'total_amount', 'created_at',
    )
    list_filter = ('status', 'payment_method', 'shipping_method')
    search_fields = ('recipient_name', 'recipient_phone', 'member__username', 'tracking_number')
    inlines = [OrderItemInline]
    actions = ['mark_as_paid', 'mark_as_returned']

    @admin.display(description='訂單狀態')
    def colored_status(self, obj):
        bg, fg = STATUS_ADMIN_COLORS.get(obj.status, ('#F1F5F9', '#475569'))
        return format_html(
            '<span style="background:{}; color:{}; padding:2px 10px; border-radius:9999px; font-size:12px;">{}</span>',
            bg, fg, obj.get_status_display(),
        )

    @admin.action(description='標記為已付款（僅套用於待付款訂單）')
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status=Order.Status.PENDING_PAYMENT).update(status=Order.Status.PAID)
        self.message_user(request, f'{updated} 筆訂單已標記為已付款')

    @admin.action(description='標記為已退貨（僅套用於退貨中訂單）')
    def mark_as_returned(self, request, queryset):
        updated = queryset.filter(status=Order.Status.RETURNING).update(status=Order.Status.RETURNED)
        self.message_user(request, f'{updated} 筆訂單已標記為已退貨')
