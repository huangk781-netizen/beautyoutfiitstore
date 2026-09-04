from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """商品分類"""

    name = models.CharField(max_length=100, unique=True, verbose_name='分類名稱')
    jp_name = models.CharField(max_length=100, blank=True, verbose_name='日文分類名稱')
    slug = models.SlugField(max_length=120, unique=True, blank=True, verbose_name='網址代稱')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '商品分類'
        verbose_name_plural = '商品分類'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品主檔"""

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products', verbose_name='分類'
    )
    name = models.CharField(max_length=200, verbose_name='商品名稱')
    jp_name = models.CharField(max_length=200, blank=True, verbose_name='日文商品名稱')
    slug = models.SlugField(max_length=220, unique=True, blank=True, verbose_name='網址代稱')
    description = models.TextField(blank=True, verbose_name='商品描述')
    jp_description = models.TextField(blank=True, verbose_name='日文商品描述')
    size_guide = models.TextField(
        blank=True,
        verbose_name='尺寸對照',
        help_text='每行輸入「尺寸代碼|對照文案」，例如 XS|32 / 70 A-B 杯。',
    )
    jp_size_guide = models.TextField(
        blank=True,
        verbose_name='日文尺寸對照',
        help_text='每行輸入「尺寸代碼|日文對照文案」，例如 M|着丈 62cm / 身幅 48cm。',
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='商品圖片')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='售價')
    is_active = models.BooleanField(default=True, verbose_name='是否上架')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    """Additional gallery images for a product."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='gallery_images', verbose_name='商品'
    )
    image = models.ImageField(upload_to='products/', verbose_name='商品圖片')
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name='顯示順序')

    class Meta:
        verbose_name = '商品圖片'
        verbose_name_plural = '商品圖片'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f'{self.product.name} 圖片 {self.pk}'


class ProductVariant(models.Model):
    """商品規格：尺寸、顏色、庫存"""

    class Size(models.TextChoices):
        XS = 'XS', 'XS'
        S = 'S', 'S'
        M = 'M', 'M'
        L = 'L', 'L'
        XL = 'XL', 'XL'
        XXL = 'XXL', 'XXL'
        FREE = 'FREE', '均一尺寸'

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='variants', verbose_name='商品'
    )
    size = models.CharField(max_length=10, choices=Size.choices, verbose_name='尺寸')
    color = models.CharField(max_length=50, verbose_name='顏色')
    jp_color = models.CharField(max_length=50, blank=True, verbose_name='日文顏色')
    sku = models.CharField(max_length=64, unique=True, verbose_name='貨號')
    stock = models.PositiveIntegerField(default=0, verbose_name='庫存數量')

    class Meta:
        verbose_name = '商品規格'
        verbose_name_plural = '商品規格'
        unique_together = ('product', 'size', 'color')

    def __str__(self):
        return f'{self.product.name} - {self.size} / {self.color}'
