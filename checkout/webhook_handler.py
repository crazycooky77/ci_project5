import json
import time
import stripe
from django.db import models as dmodels
from django.db.models import F
from django.http import HttpResponse
from products.models import ProductDetails
from profiles.forms import AddressForm
from profiles.models import OrderHistory, Addresses, User, Purchases, SavedItems
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import send_mail


def get_addresses(user, first_name, last_name, addr_details, addr_line3):
    filters = dmodels.Q(
        first_name__iexact=first_name) & dmodels.Q(
        last_name__iexact=last_name) & dmodels.Q(
        addr_line1__iexact=addr_details.address['line1']) & dmodels.Q(
        city__iexact=addr_details.address['city']) & dmodels.Q(
        eir_code__iexact=addr_details.address['postal_code']) & dmodels.Q(
        county__iexact=addr_details.address['state']) & dmodels.Q(
        phone_nr=addr_details['phone'])

    if addr_details.address['line2']:
        filters &= dmodels.Q(addr_line2__iexact=addr_details.address['line2'])

    if addr_line3:
        filters &= dmodels.Q(addr_line3__iexact=addr_line3)
    if user:
        filters &= dmodels.Q(user=user)

    addr_id = Addresses.objects.filter(filters)[:1].values_list(
        'address_id', flat=True)

    return addr_id


class StripeHWHandler:
    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        cust_email = order.purchaser_email
        subject = render_to_string(
            'confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email])

    def handle_event(self, event):
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id
        cart = intent.metadata.cart
        subtotal = intent.metadata.subtotal
        shipping_cost = intent.metadata.shipping
        grand_total = intent.metadata.grand_total
        ship_first_name = intent.metadata.ship_first_name
        ship_last_name = intent.metadata.ship_last_name
        bill_first_name = intent.metadata.bill_first_name
        bill_last_name = intent.metadata.bill_last_name

        email = intent.metadata.email
        if email == 'AnonymousUser':
            email = None
        try:
            order_note = intent.metadata.order_note
        except AttributeError:
            order_note = None
        try:
            bill_addr_line3 = intent.metadata.bill_addr_line3
        except AttributeError:
            bill_addr_line3 = None
        try:
            ship_addr_line3 = intent.metadata.ship_addr_line3
        except AttributeError:
            ship_addr_line3 = None

        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)

        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping

        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None
        if ship_addr_line3 == "":
            ship_addr_line3 = None
        for field, value in billing_details.address.items():
            if value == "":
                billing_details.address[field] = None
        if bill_addr_line3 == "":
            bill_addr_line3 = None

        if email:
            user = User.objects.get(email__iexact=email)
        else:
            user = None
        ship_addr_id = get_addresses(user, ship_first_name, ship_last_name,
                                     shipping_details, ship_addr_line3)
        bill_addr_id = get_addresses(user, bill_first_name, bill_last_name,
                                     billing_details, bill_addr_line3)

        if not email:
            email = billing_details['email']

        if not ship_addr_id:
            ship_addr_form = AddressForm(
                {'first_name': ship_first_name,
                 'last_name': ship_last_name,
                 'addr_line1':
                     shipping_details.address['line1'],
                 'addr_line2':
                     shipping_details.address['line2'],
                 'addr_line3': ship_addr_line3,
                 'city': shipping_details.address[
                     'city'],
                 'eir_code': shipping_details.address[
                     'postal_code'],
                 'county': shipping_details.address[
                     'state'],
                 'country': shipping_details.address[
                     'country'],
                 'phone_nr': shipping_details['phone'],
                 'email': email})
            s_obj = ship_addr_form.save(commit=False)
            if email:
                s_obj.user = user
            s_obj.email = email
            s_obj.addr_line3 = ship_addr_line3
            s_obj.default_addr = False
            s_obj.save()
            ship_addr_id = s_obj.pk

        if not bill_addr_id:
            bill_addr_form = AddressForm({
                'first_name': bill_first_name,
                'last_name': bill_last_name,
                'addr_line1': billing_details.address['line1'],
                'addr_line2': billing_details.address['line2'],
                'addr_line3': bill_addr_line3,
                'city': billing_details.address['city'],
                'eir_code': billing_details.address['postal_code'],
                'county': billing_details.address['state'],
                'country': billing_details.address['country'],
                'phone_nr': billing_details['phone'],
                'email': email})
            b_obj = bill_addr_form.save(commit=False)
            if email:
                b_obj.user = user
            b_obj.email = email
            b_obj.addr_line3 = bill_addr_line3
            b_obj.default_addr = False
            b_obj.save()
            bill_addr_id = b_obj.pk

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = OrderHistory.objects.get(
                    stripe_pid=pid)
                order_exists = True
                break
            except OrderHistory.DoesNotExist:
                attempt += 1
                time.sleep(1)
        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} '
                        f'| SUCCESS: Verified order already in database', status=200)
        else:
            order = None
            try:
                if user:
                    order = OrderHistory.objects.create(
                        purchaser=user,
                        purchaser_email=billing_details['email'],
                        billing_addr=Addresses.objects.get(pk=bill_addr_id),
                        shipping_addr=Addresses.objects.get(pk=ship_addr_id),
                        order_note=order_note,
                        subtotal=subtotal,
                        shipping_cost=shipping_cost,
                        grand_total=grand_total,
                        status='PEND',
                        stripe_pid=pid)
                else:
                    order = OrderHistory.objects.create(
                        purchaser_email=billing_details['email'],
                        billing_addr=Addresses.objects.get(pk=bill_addr_id),
                        shipping_addr=Addresses.objects.get(pk=ship_addr_id),
                        order_note=order_note,
                        subtotal=subtotal,
                        shipping_cost=shipping_cost,
                        grand_total=grand_total,
                        status='PEND',
                        stripe_pid=pid)
                order.save()
                for product, quantity in json.loads(cart).items():
                    Purchases.objects.create(
                        order=OrderHistory.objects.get(pk=order.pk),
                        product=ProductDetails.objects.get(pk=product),
                        quantity=quantity)
                    ProductDetails.objects.filter(
                        pk=product).update(
                        stock_count=F('stock_count') - quantity)
                if user:
                    SavedItems.objects.filter(
                        owner=user,
                        list_type='CART').delete()

            except Exception as e:
                if order:
                    order.delete()
                return HttpResponse(content=f'Webhook received: {event["type"]}'
                                            f' | ERROR: {e}', status=500)

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]}'
                    f' | SUCCESS: Created order in webhook', status=200)

    def handle_payment_intent_failed(self, event):
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)
