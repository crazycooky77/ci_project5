import json
from products.models import ProductDetails
from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from profiles.models import SavedItems
from django.contrib import messages
from django.db.models import F
from django.db import models as dmodels
from decimal import Decimal
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core import serializers
import stripe
from profiles.forms import AddressForm
from profiles.models import OrderHistory, Purchases
from .forms import *


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
                if str(prod) not in user_cart_ids_set.intersection(cart_ids_set):
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
                request, 'Your guest and account cart contents have been merged.')

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
                f'The item was not added to your cart. ' +
                'You already have the maximum possible for ' +
                'this item in your cart.')
        elif not adjusted_quantity:
            messages.success(
                request,
                f'You successfully added {quantity} items to your cart.')
        else:
            messages.success(
                request,
                f'You successfully added {adjusted_quantity} items to ' +
                'your cart. The quantity was reduced, as the items ' +
                'already in your cart, plus those you added, ' +
                'exceeded our stock.')
    else:
        if adjusted_quantity or adjusted_quantity == 0:
            messages.error(
                request,
                f'The item was not added to your cart. ' +
                'You already have the maximum possible for ' +
                'this item in your cart.')
        else:
            messages.success(
                request,
                f'You successfully added {quantity} item to your cart.')

    request.session['cart'] = cart
    redirect_url = request.POST.get('redirect_url')
    return redirect(redirect_url)


def cart_contents(request):
    if request.user.is_authenticated:
        user_cart = SavedItems.objects.filter(
            owner=request.user,
            list_type='CART')
        cart = {}
        for prod in user_cart:
            cart[str(prod.product.pk)] = prod.quantity
        request.session['cart'] = cart

    else:
        cart = request.session.get('cart', {})

    if cart:
        cart_prods = list()
        subtotal = 0

        for product in cart:
            prod_details = ProductDetails.objects.filter(pk=product)[0]
            cart_prods.append(prod_details)
            subtotal += prod_details.price * cart[product]

        if subtotal < settings.FREE_SHIPPING_THRESHOLD:
            shipping = round(subtotal * Decimal(
                settings.STANDARD_SHIPPING_PERCENTAGE)/100, 2)
        else:
            shipping = 0

        grand_total = shipping + subtotal

    else:
        cart_prods = None
        subtotal = None
        shipping = None
        grand_total = None

    return cart_prods, cart, subtotal, shipping, grand_total


def cart_view(request):
    cart_prods, cart, subtotal, shipping, grand_total = cart_contents(request)
    if cart:
        return render(request, 'cart.html',
                      {'cart_prods': zip(cart_prods, cart.values()),
                       'subtotal': subtotal,
                       'shipping': shipping,
                       'grand_total': grand_total})
    else:
        return render(request, 'cart.html')


def update_cart(request):
    cart = request.session.get('cart', {})

    loop_count = 0

    for i in request.POST:
        if request.POST.get("update-cart-button"):
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
                    request, 'You successfully removed the item from your cart')
        request.session['cart'] = cart

    if request.POST.get("empty-cart-button"):
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


def dual_addr_form(request):
    shipping_addr = json.loads(request.POST.getlist(
        'shipping-addr')[0].replace("'", '"'))
    billing_addr = json.loads(request.POST.getlist(
        'billing-addr')[0].replace("'", '"'))

    if request.user.is_authenticated:
        ship_order_addr_form = OrderFormAddr(
            initial=shipping_addr, user_auth=True)
        bill_order_addr_form = OrderFormAddr(
            initial=billing_addr, user_auth=True)
    else:
        ship_order_addr_form = OrderFormAddr(
            initial=shipping_addr)
        bill_order_addr_form = OrderFormAddr(
            initial=billing_addr)
    return ship_order_addr_form, bill_order_addr_form


def checkout_addr(request, order_addr_form):
    addr_list = Addresses.objects.filter(
        user=request.user)
    js_addr = serializers.serialize('json', addr_list,
                                    ensure_ascii=False)

    if request.POST.get('shipping-addr'):
        ship_order_addr_form, bill_order_addr_form = dual_addr_form(request)

        return ship_order_addr_form, bill_order_addr_form, addr_list, js_addr

    else:
        def_addr = Addresses.objects.filter(
            user=request.user,
            default_addr=True)
        if def_addr:
            def_addr = def_addr[0]
            order_addr_form = OrderFormAddr(initial={
                'first_name': def_addr.first_name,
                'last_name': def_addr.last_name,
                'addr_line1': def_addr.addr_line1,
                'addr_line2': def_addr.addr_line2,
                'addr_line3': def_addr.addr_line3,
                'city': def_addr.city,
                'eir_code': def_addr.eir_code,
                'county': def_addr.county,
                'country': def_addr.country,
                'phone_nr': '0' + str(def_addr.phone_nr),
                'email': def_addr.user.email},
                user_auth=True)

        return order_addr_form, addr_list, js_addr


def checkout_view(request):
    cart = request.session.get('cart', {})
    order_note = request.POST.get('checkout-order-note')

    if request.POST.get("checkout-button") or request.POST.get(
            "checkout-edit-addr"):
        if not cart:
            messages.error(
                request, "You don't have anything in your cart at the moment.")
            return redirect(reverse('all-products'))
        else:
            order_addr_form = OrderFormAddr()
            if request.POST.get('shipping-addr'):
                if request.user.is_authenticated:
                    (ship_order_addr_form, bill_order_addr_form,
                     addr_list, js_addr) = checkout_addr(
                        request, order_addr_form)
                    return render(request,
                                  'checkout_addr.html',
                                  {'ship_order_addr_form': ship_order_addr_form,
                                   'bill_order_addr_form': bill_order_addr_form,
                                   'addr_list': addr_list,
                                   'js_addr': js_addr,
                                   'order_note': order_note})
                else:
                    ship_order_addr_form, bill_order_addr_form = (
                        dual_addr_form(request))
                    return render(
                        request, 'checkout_addr.html',
                        {'ship_order_addr_form': ship_order_addr_form,
                         'bill_order_addr_form': bill_order_addr_form,
                         'order_note': order_note})

            elif request.user.is_authenticated:
                order_addr_form, addr_list, js_addr = checkout_addr(
                    request, order_addr_form)
                return render(request,
                              'checkout_addr.html',
                              {'order_addr_form': order_addr_form,
                               'addr_list': addr_list,
                               'js_addr': js_addr,
                               'order_note': order_note})
            elif ((request.POST.get("checkout-guest-button")
                  or request.POST.get("checkout-edit-addr"))
                  and not request.POST.get('shipping-addr')):
                return render(request,
                              'checkout_addr.html',
                              {'order_addr_form': order_addr_form,
                               'order_note': order_note})
            elif request.POST.get("checkout-signin-button"):
                user = authenticate(request, email=request.POST["login"],
                                    password=request.POST["password"])
                if user:
                    login(request, user)
                    messages.success(request, 'Logged in successfully')
                    SavedItems.objects.filter(owner=request.user,
                                              list_type='CART').delete()
                    for prod in cart:
                        SavedItems.objects.create(
                            owner=request.user,
                            list_type='CART',
                            product=ProductDetails.objects.get(pk=prod),
                            quantity=cart[prod])

                    if request.POST.get('shipping-addr'):
                        (ship_order_addr_form, bill_order_addr_form,
                         addr_list, js_addr) = checkout_addr(
                            request, order_addr_form)
                        return render(
                            request, 'checkout_addr.html',
                            {'ship_order_addr_form': ship_order_addr_form,
                             'bill_order_addr_form': bill_order_addr_form,
                             'addr_list': addr_list,
                             'js_addr': js_addr,
                             'order_note': order_note})
                    else:
                        order_addr_form, addr_list, js_addr = checkout_addr(
                            request, order_addr_form)
                        return render(request,
                                      'checkout_addr.html',
                                      {'order_addr_form': order_addr_form,
                                       'addr_list': addr_list,
                                       'js_addr': js_addr,
                                       'order_note': order_note})
                else:
                    messages.error(request, 'Login failed')
            else:
                return render(request,
                              'checkout_signin.html')

    elif request.POST.get("addr-form-button"):
        order_note = request.POST.get('checkout-order-note')
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        if OrderFormAddr().is_valid:
            shipping_addr = {
                'first_name': request.POST.getlist('first_name')[0],
                'last_name': request.POST.getlist('last_name')[0],
                'addr_line1': request.POST.getlist('addr_line1')[0],
                'addr_line2': request.POST.getlist('addr_line2')[0],
                'addr_line3': request.POST.getlist('addr_line3')[0],
                'city': request.POST.getlist('city')[0],
                'eir_code': request.POST.getlist('eir_code')[0],
                'county': request.POST.getlist('county')[0],
                'country': 'Ireland',
                'phone_nr': request.POST.getlist('phone_nr')[0],
                'email': request.POST.getlist('email')[0]}
            billing_addr = {
                'first_name': request.POST.getlist('first_name')[1],
                'last_name': request.POST.getlist('last_name')[1],
                'addr_line1': request.POST.getlist('addr_line1')[1],
                'addr_line2': request.POST.getlist('addr_line2')[1],
                'addr_line3': request.POST.getlist('addr_line3')[1],
                'city': request.POST.getlist('city')[1],
                'eir_code': request.POST.getlist('eir_code')[1],
                'county': request.POST.getlist('county')[1],
                'country': 'Ireland',
                'phone_nr': request.POST.getlist('phone_nr')[1],
                'email': request.POST.getlist('email')[1]}

            cart_prods, cart, subtotal, shipping, grand_total = cart_contents(
                request)
            stripe_total = round(grand_total * 100)
            stripe.api_key = stripe_secret_key
            intent = stripe.PaymentIntent.create(
                amount=stripe_total,
                currency=settings.STRIPE_CURRENCY)

            return render(request,
                          'checkout_confirm.html',
                          {'shipping_addr': shipping_addr,
                           'billing_addr': billing_addr,
                           'cart_prods': zip(cart_prods, cart.values()),
                           'subtotal': subtotal,
                           'shipping': shipping,
                           'grand_total': grand_total,
                           'order_note': order_note,
                           'stripe_public_key': stripe_public_key,
                           'client_secret': intent.client_secret})

    if request.POST.get("shipping_addr"):
        return render(request, 'checkout_addr.html',
                      {'order_note': order_note})


def format_addresses(request, addr_field):
    addr = json.loads(request.POST.get(
        addr_field).replace("'", '"'))
    addr['country'] = 'IE'

    if request.user.is_authenticated:
        addr_id = get_addresses(request.user, addr)
    else:
        addr_id = None

    return addr_id, addr


def get_addresses(user, addr):
    filters = dmodels.Q(user=user) & dmodels.Q(
        first_name__iexact=addr['first_name']) & dmodels.Q(
        last_name__iexact=addr['last_name']) & dmodels.Q(
        addr_line1__iexact=addr['addr_line1']) & dmodels.Q(
        city__iexact=addr['city']) & dmodels.Q(
        eir_code__iexact=addr['eir_code']) & dmodels.Q(
        county__iexact=addr['county']) & dmodels.Q(
        phone_nr=addr['phone_nr'])

    if addr['addr_line2']:
        filters &= dmodels.Q(addr_line2__iexact=addr['addr_line2'])

    if addr['addr_line3']:
        filters &= dmodels.Q(addr_line3__iexact=addr['addr_line3'])
    addr_id = Addresses.objects.filter(filters)[:1].values_list(
        'address_id', flat=True)

    return addr_id


def save_order_addr(request, addr):
    addr_form = AddressForm(addr)
    obj = addr_form.save(commit=False)
    if request.user.is_authenticated:
        obj.user = request.user
        obj.email = request.user.email
    else:
        obj.email = addr['email']
    obj.default_addr = False
    obj.save()
    user_addr_id = obj.pk

    return user_addr_id


def checkout_complete(request):
    if request.method == 'POST':
        user_ship_addr_id, post_shipping = format_addresses(
            request, 'shipping-addr')
        user_bill_addr_id, post_billing = format_addresses(
            request, 'billing-addr')
        order_note = request.POST.get('checkout-order-note')
        shipping_cost = request.POST.get('shipping')
        cart_prods, cart, subtotal, shipping, grand_total = (
            cart_contents(request))

        if not cart_prods:
            return render(request, 'checkout_error.html')
        if request.user.is_authenticated:
            if not user_ship_addr_id:
                user_ship_addr_id = save_order_addr(request, post_shipping)
            if not user_bill_addr_id:
                user_bill_addr_id = save_order_addr(request, post_billing)

            user_order = OrderHistory.objects.create(
                purchaser=request.user,
                purchaser_email=request.user.email,
                billing_addr=Addresses.objects.get(pk=user_bill_addr_id),
                shipping_addr=Addresses.objects.get(pk=user_ship_addr_id),
                order_note=order_note,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                grand_total=grand_total,
                status='PEND')
        else:
            user_ship_addr_id = save_order_addr(request, post_shipping)
            user_bill_addr_id = save_order_addr(request, post_billing)

            user_order = OrderHistory.objects.create(
                purchaser_email=post_billing['email'],
                billing_addr=Addresses.objects.get(pk=user_bill_addr_id),
                shipping_addr=Addresses.objects.get(pk=user_ship_addr_id),
                order_note=order_note,
                subtotal=subtotal,
                shipping_cost=shipping_cost,
                grand_total = grand_total,
                status='PEND')

        for product, quantity in zip(cart_prods, cart):
            Purchases.objects.create(
                order=OrderHistory.objects.get(pk=user_order.pk),
                product=product,
                quantity=cart[quantity])

        del request.session['cart']
        if request.user.is_authenticated:
            SavedItems.objects.filter(
                owner=request.user,
                list_type='CART').delete()
        completed_purchases = Purchases.objects.filter(
            order__order_id=user_order.pk)
        completed_order = OrderHistory.objects.get(pk=user_order.pk)

        return render(request, 'checkout_success.html',
                      {'completed_purchases': completed_purchases,
                       'completed_order': completed_order,
                       'cart_prods': zip(cart_prods, cart.values()),
                       'subtotal': subtotal,
                       'shipping': shipping,
                       'grand_total': grand_total})
    else:
        return render(request, 'checkout_error.html')