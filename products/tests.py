from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Category, Product, ProductVideo
from .views import _jpy_price_from_twd


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

    def test_jpy_price_uses_exchange_rate_and_ends_in_90(self):
        self.assertEqual(_jpy_price_from_twd(Decimal('18')), 90)
        self.assertEqual(_jpy_price_from_twd(Decimal('18.90')), 90)
        self.assertEqual(_jpy_price_from_twd(Decimal('21')), 190)
        self.assertEqual(_jpy_price_from_twd(Decimal('500')), 2390)
        self.assertEqual(_jpy_price_from_twd(Decimal('420')), 2090)

    def test_japan_landing_displays_yen_price(self):
        self.create_product(price=500)

        response = self.client.get(reverse('japan_landing'))

        self.assertContains(response, '¥2390')
        self.assertNotContains(response, 'NT$ 500')

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


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class ProductVideoTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='洋裝')
        self.product = Product.objects.create(
            category=category,
            name='影片測試商品',
            price=1280,
        )

    def test_product_video_is_rendered_in_detail_gallery(self):
        ProductVideo.objects.create(
            product=self.product,
            video='products/videos/look.mp4',
        )

        response = self.client.get(reverse('products:product_detail', args=[self.product.pk]))

        self.assertContains(response, 'data-media-type="video"')
        self.assertContains(response, 'look.mp4')
        self.assertContains(response, 'controls')

    def test_product_video_rejects_unsupported_extension(self):
        video = ProductVideo(
            product=self.product,
            video=SimpleUploadedFile('look.avi', b'video-content', content_type='video/x-msvideo'),
        )

        with self.assertRaises(ValidationError):
            video.full_clean()
