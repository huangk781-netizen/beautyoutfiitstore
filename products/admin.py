from django.contrib import admin

from .models import Category, Product, ProductVariant


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


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
    inlines = [ProductVariantInline]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'sku', 'stock')
    list_filter = ('size', 'color')
    search_fields = ('sku', 'product__name')
