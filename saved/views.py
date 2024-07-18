import json
from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.contrib import messages
from django.db.models import F
from decimal import Decimal
from django.conf import settings
from .models import *


@receiver(user_logged_in)
def cart_merge(sender, user, request, **kwargs):
    if request.POST.get('checkout-signin-button'):
        cart = request.session.get('cart', {})
        SavedItems.objects.filter(
            owner=request.user,
            list_type='CART').delete()
        for prod in cart:
            SavedItems.objects.create(
                owner=request.user,
                list_type='CART',
                product=ProductDetails.objects.get(pk=prod),
                quantity=cart[prod])
        return cart
    else:
        cart = request.session.get('cart', {})

        if request.user.is_authenticated and cart:
            user_cart = SavedItems.objects.filter(
                owner=request.user,
                list_type='CART').values_list(
                'product__pk', 'quantity')
            user_cart_ids_set = set()
            user_cart_quantity = list()
            cart_ids_set = set()

            for pk, quantity in user_cart:
                user_cart_ids_set.add(str(pk))
                user_cart_quantity.append(quantity)

            for pk in cart:
                cart_ids_set.add(str(pk))

            for prod in cart:
                if str(prod) not in user_cart_ids_set.intersection(
                        cart_ids_set):
                    user_cart, created = SavedItems.objects.get_or_create(
                        owner=request.user,
                        list_type='CART',
                        product=ProductDetails.objects.get(pk=prod),
                        defaults={'quantity': cart[prod]})
                    if not created:
                        user_cart.quantity = F('quantity') + cart[prod]

            updated_cart = SavedItems.objects.filter(owner=request.user,
                                                     list_type='CART').values()
            cart = {}
            for prod in updated_cart:
                cart[str(prod['product_id'])] = prod['quantity']
            request.session['cart'] = cart

            messages.success(
                request,
                'Your guest and account cart contents have been merged.')

            return cart

        else:
            return cart


def add_cart(request, product_id):
    request.session['active_sort'] = request.POST.get('active_sort')
    flavour = request.POST.get(product_id + '-prod-flavours')
    size = request.POST.get(product_id + '-prod-sizes')
    quantity = int(request.POST.get(product_id + '-prod-quantity'))
    adjusted_quantity = None

    if flavour:
        details_pk = str(ProductDetails.objects.filter(
            product__product_id=product_id).filter(
            flavour=flavour).filter(size=size)[0].pk)
    else:
        details_pk = str(ProductDetails.objects.filter(
            product__product_id=product_id).filter(
            size=size)[0].pk)

    if request.user.is_authenticated:
        user_cart, created = SavedItems.objects.get_or_create(
            owner=request.user,
            list_type='CART',
            product=ProductDetails.objects.get(pk=int(details_pk)),
            defaults={'quantity': quantity})
        if not created:
            if user_cart.quantity + quantity <= user_cart.product.stock_count:
                user_cart.quantity = F('quantity') + quantity
            else:
                adjusted_quantity = (
                        user_cart.product.stock_count - user_cart.quantity)
                user_cart.quantity = F('quantity') + adjusted_quantity
        user_cart.save()
        updated_cart = SavedItems.objects.filter(owner=request.user,
                                                 list_type='CART').values()
        cart = {}
        for prod in updated_cart:
            cart[str(prod['product_id'])] = prod['quantity']

    cart = request.session.get('cart', {})
    prod_stock = ProductDetails.objects.filter(pk=int(details_pk)).values_list(
        'stock_count', flat=True)[0]

    if details_pk in list(cart.keys()):
        if cart[details_pk] + quantity <= prod_stock:
            cart[details_pk] += quantity
        else:
            adjusted_quantity = prod_stock - cart[details_pk]
            cart[details_pk] += adjusted_quantity
    else:
        cart[details_pk] = quantity

    if quantity > 1:
        if adjusted_quantity == 0:
            messages.error(
                request,
                'The item was not added to your cart. ' +
                'You already have the maximum possible for ' +
                'this item in your cart.')
        elif not adjusted_quantity:
            messages.success(
                request,
                f'You successfully added {quantity} items to your cart. ' +
                '<a href="/cart">View Cart</a>')
        elif adjusted_quantity > 1:
            messages.success(
                request,
                f'You successfully added {adjusted_quantity} items to ' +
                'your cart. The quantity was reduced, as the items ' +
                'already in your cart, plus those you added, ' +
                'exceeded our stock. <a href="/cart">View Cart</a>')
        else:
            messages.success(
                request,
                f'You successfully added {adjusted_quantity} item to ' +
                'your cart. The quantity was reduced, as the items ' +
                'already in your cart, plus those you added, ' +
                'exceeded our stock. <a href="/cart">View Cart</a>')
    else:
        if adjusted_quantity or adjusted_quantity == 0:
            messages.error(
                request,
                f'The item was not added to your cart. ' +
                'You already have the maximum possible for ' +
                'this item in your cart. <a href="/cart">View Cart</a>')
        else:
            messages.success(
                request,
                f'You successfully added {quantity} item to your cart. ' +
                '<a href="/cart">View Cart</a>')

    request.session['cart'] = cart
    redirect_url = request.POST.get('redirect_url')
    return redirect(redirect_url)


def cart_contents(request):
    stock_change = None
    stock_list = list()

    if request.user.is_authenticated:
        user_cart = SavedItems.objects.filter(
            owner=request.user,
            list_type='CART')
        cart = {}
        for prod in user_cart:
            cart[str(prod.product.pk)] = prod.quantity
            if prod.quantity > prod.product.stock_count:
                if prod.product.stock_count > 0:
                    SavedItems.objects.filter(
                        owner=request.user,
                        list_type='CART',
                        product__pk=prod.product.pk).update(
                        quantity=prod.product.stock_count)
                else:
                    SavedItems.objects.filter(
                        owner=request.user,
                        list_type='CART',
                        pk=prod.pk).delete()
            if not prod.product.active:
                SavedItems.objects.filter(
                    owner=request.user,
                    list_type='CART',
                    pk=prod.pk).delete()
        request.session['cart'] = cart

    else:
        cart = request.session.get('cart', {})

    if cart:
        cart_prods = list()
        subtotal = 0

        for product in cart:
            try:
                prod_details = ProductDetails.objects.get(pk=product)
                if cart[product] > prod_details.stock_count:
                    stock_list.append(prod_details.pk)
                    cart[product] = prod_details.stock_count
                elif not prod_details.active:
                    stock_list.append(prod_details.pk)
            except ProductDetails.DoesNotExist:
                del cart[product]

        if stock_list:
            stock_change = ProductDetails.objects.filter(pk__in=stock_list)
            for prod in stock_list:
                prod_details = ProductDetails.objects.get(pk=prod)
                if prod_details.stock_count == 0:
                    del cart[str(prod_details.pk)]
                elif not prod_details.active:
                    del cart[str(prod_details.pk)]

        for product in cart:
            prod_details = ProductDetails.objects.get(pk=product)
            subtotal += prod_details.price * cart[product]
            cart_prods.append(prod_details)

        if subtotal < settings.FREE_SHIPPING_THRESHOLD:
            shipping = round(subtotal * Decimal(
                settings.STANDARD_SHIPPING_PERCENTAGE)/100, 2)
        else:
            shipping = 0

        request.session['cart'] = cart
        grand_total = shipping + subtotal

    else:
        cart_prods = None
        subtotal = None
        shipping = None
        grand_total = None

    return (cart_prods, cart, stock_change, stock_list,
            subtotal, shipping, grand_total)


def cart_view(request):
    (cart_prods, cart, stock_change, stock_list,
     subtotal, shipping, grand_total) = (
        cart_contents(request))
    checkout_empty = request.POST.get('checkout-empty')

    if cart:
        return render(request, 'cart.html',
                      {'cart_prods': zip(cart_prods, cart.values()),
                       'stock_change': stock_change,
                       'subtotal': subtotal,
                       'shipping': shipping,
                       'grand_total': grand_total})
    if checkout_empty:
        js_stock = json.loads(request.POST.get('js-stock'))
        js_stock_list = []
        for item in js_stock:
            js_stock_list.append(item['pk'])
        stock_change = ProductDetails.objects.filter(pk__in=js_stock_list)
        return render(request, 'cart.html', {
            'checkout_empty': checkout_empty,
            'stock_change': stock_change})
    else:
        return render(request, 'cart.html')


def update_cart(request):
    cart = request.session.get('cart', {})

    loop_count = 0

    for i in request.POST:
        if request.POST.get('update-cart-button'):
            if '-prod-quantity' in i:
                details_pk = i.split('-prod-quantity')[0]
                for prod in cart:
                    if prod == details_pk:
                        quantity = int(request.POST.get(i))
                        cart[details_pk] = quantity
                        if request.user.is_authenticated:
                            user_cart = SavedItems.objects.get(
                                owner=request.user,
                                list_type='CART',
                                product__pk=int(details_pk))
                            user_cart.quantity = quantity
                            user_cart.save()
                        loop_count += 1
                        if loop_count == 1:
                            messages.success(
                                request, 'You successfully updated your cart')
        elif '-prod-del' in i:
            details_pk = i.split('-prod-del')[0]
            del cart[details_pk]
            if request.user.is_authenticated:
                user_cart = SavedItems.objects.get(
                    owner=request.user,
                    list_type='CART',
                    product__pk=int(details_pk))
                user_cart.delete()
            loop_count += 1
            if loop_count == 1:
                messages.success(
                    request,
                    'You successfully removed the item from your cart')
        request.session['cart'] = cart

    if request.POST.get('empty-cart-button'):
        del request.session['cart']
        if request.user.is_authenticated:
            user_cart = SavedItems.objects.filter(
                owner=request.user,
                list_type='CART')
            user_cart.delete()
        messages.success(
            request, 'You successfully emptied your cart')

    redirect_url = request.POST.get('redirect_url')
    return redirect(redirect_url)
