from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Category, Product, ProductImage, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductImageInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        primary_image_count = 1 if self.instance.image else 0
        gallery_image_count = sum(
            1
            for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get('DELETE', False)
            and (form.cleaned_data.get('image') or form.instance.image)
        )
        if primary_image_count + gallery_image_count > 10:
            raise ValidationError('每個商品最多只能有 10 張圖片，包含商品主圖。')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    formset = ProductImageInlineFormSet
    extra = 1
    max_num = 10
    fields = ('image', 'sort_order')
    verbose_name = '附加商品圖片'
    verbose_name_plural = '附加商品圖片（商品主圖加上附加圖片最多 10 張）'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'sku', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('sku', 'product__name')
