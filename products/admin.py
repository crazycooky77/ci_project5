from django.contrib import admin
from .models import *


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    """Admin site registration for Products model"""
    ordering = ['brand', 'product_name']


@admin.register(ProductDetails)
class ProductDetailsAdmin(admin.ModelAdmin):
    """Admin site registration for ProductDetails model"""
    ordering = ['product__brand', 'product__product_name']
