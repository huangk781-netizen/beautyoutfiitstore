from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from django.forms.models import BaseInlineFormSet
from django.db.models import Max

from .models import Category, Product, ProductImage, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class MultipleImageInput(forms.FileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    widget = MultipleImageInput

    def clean(self, data, initial=None):
        if not data:
            return []
        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleImageField, self).clean(image, initial) for image in files]


class ProductAdminForm(forms.ModelForm):
    image = MultipleImageField(
        required=False,
        label='商品圖片',
        help_text='可一次選取多張不同圖片。第一張會設為主圖，全部合計最多 10 張。',
        widget=MultipleImageInput(attrs={'accept': 'image/*'}),
    )

    class Meta:
        model = Product
        fields = '__all__'

    def clean_image(self):
        uploads = self.cleaned_data['image']
        primary_image_count = 1 if uploads or self.instance.image else 0
        existing_gallery_count = self.instance.gallery_images.count() if self.instance.pk else 0
        additional_image_count = max(len(uploads) - 1, 0)
        if primary_image_count + existing_gallery_count + additional_image_count > 10:
            raise ValidationError('主圖與附加圖片合計最多只能有 10 張。')
        self.additional_images = uploads[1:]
        return uploads[0] if uploads else self.instance.image


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
    extra = 0
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
    form = ProductAdminForm
    list_display = ('name', 'category', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        uploads = getattr(form, 'additional_images', [])
        if not uploads:
            return

        latest_sort_order = (
            form.instance.gallery_images.aggregate(latest=Max('sort_order'))['latest'] or 0
        )
        for offset, image in enumerate(uploads, start=1):
            ProductImage.objects.create(
                product=form.instance,
                image=image,
                sort_order=latest_sort_order + offset,
            )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'sku', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('sku', 'product__name')
