import datetime
import json
import time
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from products.models import ProductDetails
from django.shortcuts import render, redirect
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from profiles.models import SavedItems, Purchases
from django.contrib import messages
from django.db.models import F
from decimal import Decimal
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core import serializers
import stripe
from profiles.models import OrderHistory
from .forms import *


@require_POST
def cache_checkout_data(request):
    try:
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'cart': json.dumps(request.session.get('cart', {})),
            'order_note': request.POST.get('order_note'),
            'subtotal': request.POST.get('subtotal'),
            'shipping': request.POST.get('shipping'),
            'grand_total': request.POST.get('grand_total'),
            'email': request.user,
            'ship_first_name': request.POST.get('ship_first_name'),
            'bill_first_name': request.POST.get('bill_first_name'),
            'ship_last_name': request.POST.get('ship_last_name'),
            'bill_last_name': request.POST.get('bill_last_name'),
            'ship_addr_line3': request.POST.get('ship_addr_line3'),
            'bill_addr_line3': request.POST.get('bill_addr_line3')
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be '
                                'processed right now. Please try again later.')
        return HttpResponse(content=e, status=400)


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
        form_addr = None
        if def_addr:
            form_addr = def_addr[0]
        elif not def_addr and addr_list:
            form_addr = addr_list.last()
        if form_addr:
            order_addr_form = OrderFormAddr(initial={
                'first_name': form_addr.first_name,
                'last_name': form_addr.last_name,
                'addr_line1': form_addr.addr_line1,
                'addr_line2': form_addr.addr_line2,
                'addr_line3': form_addr.addr_line3,
                'city': form_addr.city,
                'eir_code': form_addr.eir_code,
                'county': form_addr.county,
                'country': form_addr.country,
                'phone_nr': '0' + str(form_addr.phone_nr),
                'email': form_addr.user.email},
                user_auth=True)

        return order_addr_form, addr_list, js_addr


def checkout_view(request):
    cart = request.session.get('cart', {})
    order_note = request.POST.get('checkout-order-note')

    if request.POST.get("checkout-button") or request.POST.get(
            "checkout-edit-addr"):
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

    elif (request.POST.get("addr-form-button")
          or request.POST.get("check-stock")):
        (cart_prods, cart, stock_change, stock_list,
         subtotal, shipping, grand_total) = (
            cart_contents(request))

        if stock_change:
            js_stock = serializers.serialize('json', stock_change,
                                             ensure_ascii=False,
                                             fields='pk')
        else:
            js_stock = ''

        check_stock = request.POST.get("check-stock")
        order_note = request.POST.get('checkout-order-note')
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        if OrderFormAddr().is_valid:
            if request.POST.get('shipping-addr'):
                shipping_addr = json.loads(request.POST.get(
                    'shipping-addr').replace("'", '"'))
                billing_addr = json.loads(request.POST.get(
                    'billing-addr').replace("'", '"'))
            else:
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

            stripe_total = round(grand_total * 100)
            stripe.api_key = stripe_secret_key

            if stock_change and cart:
                stock_change = ProductDetails.objects.filter(
                    pk__in=stock_list)
                intent = stripe.SetupIntent.create(
                    description="stock_change",
                    usage="on_session")
            elif not cart:
                intent = stripe.SetupIntent.create(
                    description="empty_cart",
                    usage="on_session")
            elif check_stock and cart and not stock_change:
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY)
            else:
                intent = stripe.SetupIntent.create()

            return render(request,
                          'checkout_confirm.html',
                          {'shipping_addr': shipping_addr,
                           'billing_addr': billing_addr,
                           'cart_prods': zip(cart_prods, cart.values()),
                           'stock_change': stock_change,
                           'js_stock': js_stock,
                           'check_stock': check_stock,
                           'subtotal': subtotal,
                           'shipping': shipping,
                           'grand_total': grand_total,
                           'order_note': order_note,
                           'stripe_public_key': stripe_public_key,
                           'client_secret': intent.client_secret})

    if request.POST.get("shipping-addr"):
        return render(request, 'checkout_addr.html',
                      {'order_note': order_note})


def checkout_complete(request):
    order_exists = False
    attempt = 1
    while attempt <= 10:
        try:
            pid = request.POST.get(
                'client-secret').split('"')[1].split('_secret')[0]
            completed_order = OrderHistory.objects.get(stripe_pid=pid)
            order_exists = True
            break
        except OrderHistory.DoesNotExist:
            attempt += 1
            time.sleep(2)
    if order_exists:
        cart = request.session['cart']
        cart_prods = list()
        for product in cart:
            prod_details = ProductDetails.objects.get(pk=product)
            cart_prods.append(prod_details)

        subtotal = completed_order.subtotal
        shipping = completed_order.shipping_cost
        grand_total = completed_order.grand_total

        del request.session['cart']

        return render(request, 'checkout_success.html',
                      {'completed_order': completed_order,
                       'cart_prods': zip(cart_prods, cart.values()),
                       'subtotal': subtotal,
                       'shipping': shipping,
                       'grand_total': grand_total})
    else:
        client_secret = request.POST.get('client-secret')

        if client_secret:
            del request.session['cart']
            if request.user.is_authenticated:
                SavedItems.objects.filter(
                    owner=request.user,
                    list_type='CART').delete()

            pid = request.POST.get(
                'client-secret').split('"')[1].split('_secret')[0]
            time_now = datetime.datetime.now()

            def _send_order_error_email(client_secret, pid):
                admin_email = settings.CONTACT_EMAIL
                subject = render_to_string(
                    'error_emails/admin_order_error_email_subject.txt',
                    {'time_now': time_now})
                body = render_to_string(
                    'error_emails/admin_order_error_email_body.txt',
                    {'client_secret': client_secret,
                     'pid': pid,
                     'time_now': time_now})
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_email])

            _send_order_error_email(client_secret, pid)

        return render(request, 'checkout_error.html',
                      {'client_secret': client_secret})
