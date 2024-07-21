import datetime
import json
import time
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.shortcuts import render
from saved.models import SavedItems
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core import serializers
import stripe
from saved.views import cart_contents
from .forms import *
from .models import *


@require_POST
def cache_checkout_data(request):
    """Get payment and order details necessary for checkout"""
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


def profile_orders(request, var):
    """View to display orders in profile for logged-in users"""
    if request.user.is_authenticated:
        order = OrderHistory.objects.filter(
            purchaser=request.user,
            pk=var)
        if order:
            order_details = Purchases.objects.filter(
                order=order[0]).order_by('product__product_id')
            products = ProductDetails.objects.filter(
                product__product_id__in=order_details.values(
                    'product__product_id')).order_by('product_id')
            return render(request, 'profile.html',
                          {'order': order[0],
                           'order_details': zip(order_details, products)})
    return render(request, 'profile.html')


def dual_addr_form(request, shipping_addr, billing_addr):
    """Generate form fields for both shipping and billing addresses
    for checkout process"""
    if isinstance(shipping_addr, Addresses):
        ship_order_addr_form = OrderFormAddr(
            instance=shipping_addr,
            prefix='ship')
        bill_order_addr_form = OrderFormAddr(
            instance=billing_addr,
            prefix='bill')
    elif request.user.is_authenticated:
        ship_order_addr_form = OrderFormAddr(
            initial=shipping_addr,
            user_auth=True,
            prefix='ship')
        bill_order_addr_form = OrderFormAddr(
            initial=billing_addr,
            user_auth=True,
            prefix='bill')
    else:
        ship_order_addr_form = OrderFormAddr(
            initial=shipping_addr,
            prefix='ship')
        bill_order_addr_form = OrderFormAddr(
            initial=billing_addr,
            prefix='bill')
    return ship_order_addr_form, bill_order_addr_form


def checkout_addr(request, ship_order_addr_form, bill_order_addr_form):
    """Get data for Checkout Address view"""
    # For logged in users, get saved addresses
    if request.user.is_authenticated:
        addr_list = Addresses.objects.filter(
            user=request.user)
        js_addr = serializers.serialize('json', addr_list,
                                        ensure_ascii=False)
        def_addr = Addresses.objects.filter(
            user=request.user,
            default_addr=True)
    else:
        addr_list = Addresses.objects.none()
        js_addr = ''
        def_addr = Addresses.objects.none()

    # Autofill address form
    if request.POST.get('shipping-addr'):
        shipping_addr = json.loads(request.POST.getlist(
            'shipping-addr')[0].replace("'", '"'))
        billing_addr = json.loads(request.POST.getlist(
            'billing-addr')[0].replace("'", '"'))

        ship_order_addr_form, bill_order_addr_form = dual_addr_form(
            request, shipping_addr, billing_addr)
    else:
        form_addr = None
        if def_addr:
            form_addr = def_addr[0]
        elif not def_addr and addr_list:
            form_addr = addr_list.last()
        if form_addr:
            ship_order_addr_form = form_addr
            bill_order_addr_form = form_addr
            ship_order_addr_form, bill_order_addr_form = dual_addr_form(
                request, ship_order_addr_form, bill_order_addr_form)

    return ship_order_addr_form, bill_order_addr_form, addr_list, js_addr


def checkout_view(request):
    """Main function for all checkout page views"""
    cart = request.session.get('cart', {})
    order_note = request.POST.get('checkout-order-note')
    # Create initial checkout address forms
    ship_order_addr_form = OrderFormAddr(prefix='ship')
    bill_order_addr_form = OrderFormAddr(prefix='bill')
    # Get data for checkout address, where available
    (ship_order_addr_form, bill_order_addr_form,
     addr_list, js_addr) = checkout_addr(
        request, ship_order_addr_form, bill_order_addr_form)

    # Initial checkout page
    if request.POST.get('checkout-button'):
        # Guest Checkout
        if (request.POST.get('checkout-guest-button') or
                request.user.is_authenticated):
            # Autofill address form details where available
            (ship_order_addr_form, bill_order_addr_form,
             addr_list, js_addr) = checkout_addr(
                request, ship_order_addr_form, bill_order_addr_form)
            return render(
                request, 'checkout-addr.html',
                {'ship_order_addr_form': ship_order_addr_form,
                 'bill_order_addr_form': bill_order_addr_form,
                 'addr_list': addr_list,
                 'js_addr': js_addr,
                 'order_note': order_note})
        # Sign-in action during checkout
        elif request.POST.get('checkout-signin-button'):
            user = authenticate(request, email=request.POST['login'],
                                password=request.POST['password'])
            # Get user/cart details for sign-in, show checkout address view
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
                # Autofill address form details where available
                (ship_order_addr_form, bill_order_addr_form,
                 addr_list, js_addr) = checkout_addr(
                    request, ship_order_addr_form, bill_order_addr_form)
                return render(
                    request, 'checkout-addr.html',
                    {'ship_order_addr_form': ship_order_addr_form,
                     'bill_order_addr_form': bill_order_addr_form,
                     'addr_list': addr_list,
                     'js_addr': js_addr,
                     'order_note': order_note})
            # Error for unsuccessful sign-in
            else:
                messages.error(request, 'Login failed')
                return render(request,
                              'checkout-signin.html')
        # Render checkout sign-in if no other scenarios apply
        else:
            return render(request, 'checkout-signin.html')
    # After user submits checkout address, or "check-stock" is in POST
    elif (request.POST.get('addr-form-button')
          or request.POST.get('check-stock')):
        (cart_prods, cart, stock_change, stock_list,
         subtotal, shipping, grand_total) = (
            cart_contents(request))

        if stock_change:
            js_stock = serializers.serialize('json', stock_change,
                                             ensure_ascii=False,
                                             fields='pk')
        else:
            js_stock = ''

        check_stock = request.POST.get('check-stock')
        order_note = request.POST.get('checkout-order-note')
        stripe_public_key = settings.STRIPE_PUBLIC_KEY
        stripe_secret_key = settings.STRIPE_SECRET_KEY

        # If address details are valid...
        if OrderFormAddr().is_valid:
            # Save address details to variables
            if request.POST.get('shipping-addr'):
                shipping_addr = json.loads(request.POST.get(
                    'shipping-addr').replace("'", '"'))
                billing_addr = json.loads(request.POST.get(
                    'billing-addr').replace("'", '"'))
            else:
                shipping_addr = {
                    'first_name': request.POST.get('ship-first_name'),
                    'last_name': request.POST.get('ship-last_name'),
                    'addr_line1': request.POST.get('ship-addr_line1'),
                    'addr_line2': request.POST.get('ship-addr_line2'),
                    'addr_line3': request.POST.get('ship-addr_line3'),
                    'city': request.POST.get('ship-city'),
                    'eir_code': request.POST.get('ship-eir_code'),
                    'county': request.POST.get('ship-county'),
                    'country': 'Ireland',
                    'phone_nr': request.POST.get('ship-phone_nr'),
                    'email': request.POST.get('ship-email')}
                billing_addr = {
                    'first_name': request.POST.get('bill-first_name'),
                    'last_name': request.POST.get('bill-last_name'),
                    'addr_line1': request.POST.get('bill-addr_line1'),
                    'addr_line2': request.POST.get('bill-addr_line2'),
                    'addr_line3': request.POST.get('bill-addr_line3'),
                    'city': request.POST.get('bill-city'),
                    'eir_code': request.POST.get('bill-eir_code'),
                    'county': request.POST.get('bill-county'),
                    'country': 'Ireland',
                    'phone_nr': request.POST.get('bill-phone_nr'),
                    'email': request.POST.get('bill-email')}

            # Get stripe data
            stripe_total = round(grand_total * 100)
            stripe.api_key = stripe_secret_key

            # Get cart and stock information and create stripe intent
            if stock_change and cart:
                # For cart changes, create SetupIntent for user to confirm cart
                stock_change = ProductDetails.objects.filter(
                    pk__in=stock_list)
                intent = stripe.SetupIntent.create(
                    description='stock_change',
                    usage='on_session')
            elif not cart:
                # If cart is now empty, create SetupIntent with "empty_cart"
                intent = stripe.SetupIntent.create(
                    description='empty_cart',
                    usage='on_session')
            elif check_stock and cart and not stock_change:
                # If stock checked, cart present, no changes > PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY)
            else:
                # For all other scenarios, create only a SetupIntent
                intent = stripe.SetupIntent.create()

            # Render to view for JS to take over actions based on Stripe data
            return render(request,
                          'checkout-confirm.html',
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
    # For all other address scenarios, display checkout address, autofill form
    else:
        return render(request,
                      'checkout-addr.html',
                      {'ship_order_addr_form': ship_order_addr_form,
                       'bill_order_addr_form': bill_order_addr_form,
                       'addr_list': addr_list,
                       'js_addr': js_addr,
                       'order_note': order_note})


def checkout_complete(request):
    """View for completed checkout process"""
    client_secret = request.POST.get('client-secret')
    cart = request.session.get('cart')

    # For seamless checkouts
    if client_secret and cart:
        order_exists = False
        attempt = 1
        # Get order details created by webhook
        while attempt <= 10:
            try:
                try:
                    pid = client_secret.split('"')[1].split('_secret')[0]
                except AttributeError:
                    pid = None
                completed_order = OrderHistory.objects.get(stripe_pid=pid)
                order_exists = True
                break
            except OrderHistory.DoesNotExist:
                attempt += 1
                time.sleep(2)
        # Once order is found, get necessary data for completed order
        if order_exists:
            cart_prods = list()
            for product in cart:
                prod_details = ProductDetails.objects.get(pk=product)
                cart_prods.append(prod_details)

            subtotal = completed_order.subtotal
            shipping = completed_order.shipping_cost
            grand_total = completed_order.grand_total

            # Delete session cart
            del request.session['cart']

            return render(request, 'checkout-success.html',
                          {'completed_order': completed_order,
                           'cart_prods': zip(cart_prods, cart.values()),
                           'subtotal': subtotal,
                           'shipping': shipping,
                           'grand_total': grand_total})
        # If no order is found
        else:
            # Delete session and user cart (if logged in)
            del request.session['cart']
            if request.user.is_authenticated:
                SavedItems.objects.filter(
                    owner=request.user,
                    list_type='CART').delete()

            # Get PaymentIntent ID and current time
            pid = request.POST.get(
                'client-secret').split('"')[1].split('_secret')[0]
            time_now = datetime.datetime.now()

            def _send_order_error_email(client_secret, pid):
                """Function to send email to admin for order errors"""
                admin_email = settings.CONTACT_EMAIL
                subject = render_to_string(
                    'error_emails/admin-order-error-email-subject.txt',
                    {'time_now': time_now})
                body = render_to_string(
                    'error_emails/admin-order-error-email-body.txt',
                    {'client_secret': client_secret,
                     'pid': pid,
                     'time_now': time_now})
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_email])

            # Send email to admin, due to order error
            _send_order_error_email(client_secret, pid)

            # Render view to user for checkout error with successful payment
            return render(request, 'checkout-error.html',
                          {'client_secret': client_secret,
                           'cart': True})
    # If user refreshes page after successful checkout, display custom error
    elif client_secret and not cart:
        return render(request, 'checkout-error.html',
                      {'client_secret': client_secret,
                       'cart': False})
    # If user access page at any other time, display custom error
    else:
        return render(request, 'checkout-error.html')
