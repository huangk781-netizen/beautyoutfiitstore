from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class JapanLandingQoo10Tests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='上衣', jp_name='トップス')

    def create_product(self, **overrides):
        values = {
            'category': self.category,
            'name': '測試上衣',
            'jp_name': 'テストトップス',
            'price': 500,
        }
        values.update(overrides)
        return Product.objects.create(**values)

    def test_product_with_qoo10_url_links_to_listing(self):
        qoo10_url = 'https://www.qoo10.jp/g/123456789'
        self.create_product(qoo10_url=qoo10_url)

        response = self.client.get(reverse('japan_landing'))

        self.assertContains(response, qoo10_url)
        self.assertContains(response, 'Qoo10で購入')

    def test_product_without_qoo10_url_shows_preparing_state(self):
        self.create_product()

        response = self.client.get(reverse('japan_landing'))

        self.assertContains(response, 'Qoo10販売準備中')
        self.assertNotContains(response, 'Qoo10で購入')
