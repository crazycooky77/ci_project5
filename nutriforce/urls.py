"""
URL configuration for nutriforce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from nutriforce_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage_view, name='home'),
    path('email/', CustomEmailChangeView.as_view(), name='email-change'),
    path('confirm-email/', CustomEmailVerificationSent.as_view(), name='verify-email'),
    re_path(r"^confirm-email/(?P<key>[-:\w]+)/$", CustomEmailConfirmView.as_view(), name='email-confirm'),
    path('password/change/', CustomPasswordChangeView.as_view(), name='pw-change'),
    path('', include('allauth.urls'), name='login'),
    path('profile', profile_view, name='profile'),
    path('profile/addresses', profile_view, name='addresses'),
    path('profile/add-address', profile_addr, name='add-address'),
    path('profile/edit-address/<var>', profile_edit_addr, name='edit-address'),
    path('orders', profile_view, name='orders'),
    path('orders/id=<var>', profile_orders, name='order-details'),
    path('products/id=<var>', product_view, name='products'),
    path('products/all', all_products, name='all-products'),
    path('products/sports', sports_products, name='sports-products'),
    path('products/health', health_products, name='health-products'),
    path('products/new', new_products, name='new-products'),
    path('cart', cart_view, name='cart'),
    path('add/<product_id>', add_cart, name='add-cart')
]
