from django.contrib import admin
from .models import Category, Product, ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'selling_price',
        'stock',
        'is_active',
    )

    search_fields = ('name', 'sku')
    list_filter = ('category', 'is_active')

    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'alt_text', 'created_at')