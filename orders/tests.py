from django.test import TestCase
from django.urls import reverse

from accounts.models import Member
from products.models import Category, Product, ProductVariant

from .models import Order


class CheckoutPaymentMethodTests(TestCase):
    def setUp(self):
        self.member = Member.objects.create_user(
            username='customer',
            password='test-password',
        )
        category = Category.objects.create(name='上衣')
        product = Product.objects.create(
            category=category,
            name='測試上衣',
            price=500,
        )
        self.variant = ProductVariant.objects.create(
            product=product,
            size=ProductVariant.Size.M,
            color='白色',
            sku='TEST-001',
            stock=5,
        )
        self.client.force_login(self.member)

    def add_item_to_cart(self):
        session = self.client.session
        session['cart'] = {str(self.variant.pk): {'quantity': 1}}
        session.save()

    def test_checkout_only_offers_cash_on_delivery(self):
        self.add_item_to_cart()

        response = self.client.get(reverse('orders:checkout'))

        self.assertContains(response, '貨到付款')
        self.assertNotContains(response, 'ATM/銀行匯款')
        self.assertContains(response, 'value="cod"', html=False)

    def test_checkout_rejects_bank_transfer_submitted_directly(self):
        self.add_item_to_cart()

        response = self.client.post(reverse('orders:checkout'), {
            'checkout_action': 'place_order',
            'recipient_name': '王小明',
            'recipient_phone': '0912345678',
            'store_name': '7-11 中正門市',
            'payment_method': Order.PaymentMethod.BANK_TRANSFER,
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '目前僅開放貨到付款')
        self.assertFalse(Order.objects.exists())
