from django.contrib import admin
from .models import *


# Admin site models
@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    ordering = ['brand', 'product_name']


@admin.register(ProductDetails)
class ProductDetailsAdmin(admin.ModelAdmin):
    ordering = ['product__brand', 'product__product_name']
