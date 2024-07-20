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


def dual_addr_form(request):
    """Generate form fields for both shipping and billing addresses
    for checkout process"""
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
    """Addresses view for checkout"""
    addr_list = Addresses.objects.filter(
        user=request.user)
    js_addr = serializers.serialize('json', addr_list,
                                    ensure_ascii=False)

    # Autofill address form
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
                'phone_nr': str(form_addr.phone_nr),
                'email': form_addr.user.email},
                user_auth=True)

        return order_addr_form, addr_list, js_addr


def checkout_view(request):
    """Main function for all checkout page views"""
    cart = request.session.get('cart', {})
    order_note = request.POST.get('checkout-order-note')

    # Views for checkout (from cart), or Edit Address button (from checkout)
    if request.POST.get('checkout-button') or request.POST.get(
            'checkout-edit-addr'):
        order_addr_form = OrderFormAddr()
        # If a shipping address in POST request, display checkout address view
        if request.POST.get('shipping-addr'):
            # Get address details to autofill form fields
            if request.user.is_authenticated:
                (ship_order_addr_form, bill_order_addr_form,
                 addr_list, js_addr) = checkout_addr(
                    request, order_addr_form)
                return render(request,
                              'checkout-addr.html',
                              {'ship_order_addr_form': ship_order_addr_form,
                               'bill_order_addr_form': bill_order_addr_form,
                               'addr_list': addr_list,
                               'js_addr': js_addr,
                               'order_note': order_note})

            else:
                ship_order_addr_form, bill_order_addr_form = (
                    dual_addr_form(request))
                return render(
                    request, 'checkout-addr.html',
                    {'ship_order_addr_form': ship_order_addr_form,
                     'bill_order_addr_form': bill_order_addr_form,
                     'order_note': order_note})

        # If user is logged in, display autofilled form fields in address view
        elif request.user.is_authenticated:
            order_addr_form, addr_list, js_addr = checkout_addr(
                request, order_addr_form)
            return render(request,
                          'checkout-addr.html',
                          {'order_addr_form': order_addr_form,
                           'addr_list': addr_list,
                           'js_addr': js_addr,
                           'order_note': order_note})
        # Guest Checkout/edit_addr w/o no ship_addr in POST: checkout addr view
        elif ((request.POST.get('checkout-guest-button')
              or request.POST.get('checkout-edit-addr'))
              and not request.POST.get('shipping-addr')):
            return render(request,
                          'checkout-addr.html',
                          {'order_addr_form': order_addr_form,
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

                # Autofill address details if Edit Address was clicked
                if request.POST.get('shipping-addr'):
                    (ship_order_addr_form, bill_order_addr_form,
                     addr_list, js_addr) = checkout_addr(
                        request, order_addr_form)
                    return render(
                        request, 'checkout-addr.html',
                        {'ship_order_addr_form': ship_order_addr_form,
                         'bill_order_addr_form': bill_order_addr_form,
                         'addr_list': addr_list,
                         'js_addr': js_addr,
                         'order_note': order_note})
                # Otherwise just display address forms with default data
                else:
                    order_addr_form, addr_list, js_addr = checkout_addr(
                        request, order_addr_form)
                    return render(request,
                                  'checkout-addr.html',
                                  {'order_addr_form': order_addr_form,
                                   'addr_list': addr_list,
                                   'js_addr': js_addr,
                                   'order_note': order_note})
            # Error for unsuccessful sign-in
            else:
                messages.error(request, 'Login failed')
        # Display sign-in/guest checkout options for checkout
        else:
            return render(request,
                          'checkout-signin.html')
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

    # Edit Address at checkout confirm, send data to checkout address view
    if request.POST.get('shipping-addr'):
        return render(request, 'checkout-addr.html',
                      {'order_note': order_note})


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
