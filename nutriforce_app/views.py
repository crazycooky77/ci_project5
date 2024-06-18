from decimal import Decimal

import pytz
from django.core import serializers
from allauth.account.views import PasswordChangeView, EmailView, \
    ConfirmEmailView, EmailVerificationSentView
from django.urls import reverse_lazy

from nutriforce import settings
from .models import *
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth import logout
import operator
import datetime
from django.db.models import Q
from django.db.models.functions import Lower
from functools import reduce
from .forms import *


def product_sort(request, data):
    sorted_data = data.order_by(
        '-stock_count').values_list(
        'product__product_id', flat=True)
    if request.GET:
        if 'sort' in request.GET:
            sort = request.GET['sort']

            if sort == 'sale':
                sorted_data = data.filter(
                    product__categories__icontains='sale').values_list(
                    'product__product_id', flat=True)

            if 'dirn' in request.GET:
                dirn = request.GET['dirn']
                if sort == 'brand':
                    if dirn == 'asc':
                        sorted_data = data.order_by(
                            Lower('product__brand')).values_list(
                            'product__product_id', flat=True)
                    elif dirn == 'desc':
                        sorted_data = data.order_by(
                            Lower('product__brand').desc()).values_list(
                            'product__product_id', flat=True)
                if sort == 'prod':
                    if dirn == 'asc':
                        sorted_data = data.order_by(
                            Lower('product__product_name')).values_list(
                            'product__product_id', flat=True)
                    elif dirn == 'desc':
                        sorted_data = data.order_by(
                            Lower('product__product_name').desc()).values_list(
                            'product__product_id', flat=True)
                if sort == 'price':
                    if dirn == 'asc':
                        sorted_data = data.order_by(
                            'price').values_list(
                            'product__product_id', flat=True)
                    elif dirn == 'desc':
                        sorted_data = data.order_by(
                            '-price').values_list(
                            'product__product_id', flat=True)

            sorted_data = list(dict.fromkeys(sorted_data))
            return sorted_data
        else:
            sorted_data = list(dict.fromkeys(sorted_data))
            return sorted_data

    sorted_data = list(dict.fromkeys(sorted_data))
    return sorted_data


def product_pages(request, qs):
    json_serializer = serializers.get_serializer("json")()
    js_products = json_serializer.serialize(qs.order_by('-stock_count'),
                                            ensure_ascii=False)
    products_sorted = product_sort(request, qs)
    product_list = ProductDetails.objects.filter(
        product_id__in=products_sorted).distinct('product_id')
    products_distinct = list()
    for product_id in products_sorted:
        products_distinct.append(product_list.get(product_id=product_id))

    return products_distinct, js_products


def homepage_view(request):
    products = ProductDetails.objects.all().exclude(active=False)
    json_serializer = serializers.get_serializer("json")()

    if ProductDetails.objects.all().exclude(pk=0).filter(stock_count__gte=10):
        new_product = ProductDetails.objects.all().exclude(pk=0).filter(
            stock_count__gte=10).latest('created_ts')
    elif ProductDetails.objects.all().exclude(pk=0):
        new_product = ProductDetails.objects.all().exclude(pk=0).latest(
            'created_ts')
    else:
        new_product = ProductDetails.objects.all().exclude(pk=0)
    sports_product = ProductDetails.objects.all().exclude(pk=0).filter(
        product__categories__icontains='sports').order_by(
        '-stock_count').first()
    health_product = ProductDetails.objects.all().exclude(pk=0).filter(
        product__categories__icontains='health').order_by(
        '-stock_count').first()

    if new_product:
        new_product_extras = ProductDetails.objects.all().filter(
            product__product_id=new_product.product_id)
        js_new_product = json_serializer.serialize(
            new_product_extras.order_by('flavour'),
            ensure_ascii=False)
    else:
        new_product_extras = ''
        js_new_product = ''

    if sports_product:
        sports_product_extras = ProductDetails.objects.all().filter(
            product__product_id=sports_product.product_id)
        js_sports_product = json_serializer.serialize(
            sports_product_extras.order_by('flavour'),
            ensure_ascii=False)
    else:
        sports_product_extras = ''
        js_sports_product = ''
    if health_product:
        health_product_extras = ProductDetails.objects.all().filter(
            product__product_id=health_product.product_id)
        js_health_product = json_serializer.serialize(
            health_product_extras.order_by('flavour'),
            ensure_ascii=False)
    else:
        health_product_extras = ''
        js_health_product = ''

    if new_product == sports_product and new_product != '' and sports_product != '':
        sports_product = ProductDetails.objects.all().exclude(pk=0).filter(
            product__categories__icontains='sports').order_by(
            '-stock_count')[1]
        sports_product_extras = ProductDetails.objects.all().filter(
            product__product_id=sports_product.product_id)
    if new_product == health_product and new_product != '' and health_product != '':
        health_product = ProductDetails.objects.all().exclude(pk=0).filter(
            product__categories__icontains='health').order_by(
            '-stock_count')[1]
        health_product_extras = ProductDetails.objects.all().filter(
            product__product_id=health_product.product_id)

    return render(request, 'index.html',
                  {'products': products,
                   'new_product': new_product,
                   'new_product_extras': new_product_extras,
                   'sports_product': sports_product,
                   'sports_product_extras': sports_product_extras,
                   'health_product': health_product,
                   'health_product_extras': health_product_extras,
                   'js_new_product': js_new_product,
                   'js_sports_product': js_sports_product,
                   'js_health_product': js_health_product})


class CreateUser(CreateView):
    model = User
    fields = ['email', 'password']
    template_name = 'account/signup.html'
    success_url = reverse_lazy('home')


class CustomEmailVerificationSent(EmailVerificationSentView):
    template_name = 'account/verification_sent.html'


class CustomEmailChangeView(EmailView):
    template_name = 'profile.html'


class CustomEmailConfirmView(ConfirmEmailView):
    template_name = 'profile.html'


class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'profile.html'


def product_view(request, var):
    product = ProductDetails.objects.all().exclude(active=False).filter(
        product__product_id=var)
    json_serializer = serializers.get_serializer("json")()
    js_product = json_serializer.serialize(product.order_by('size', 'flavour'),
                                           ensure_ascii=False)
    product_cats = Products.objects.all().filter(product_id=var)

    if product_cats:
        categories = product_cats[0].categories.split(',')
        categories = [cat.strip(' ') for cat in categories]
        for cat in categories:
            cat.strip()
        if 'health' in categories:
            categories.remove('health')
        if 'sports' in categories:
            categories.remove('sports')

        if categories:
            linked_products = ProductDetails.objects.all().exclude(
                active=False).exclude(stock_count__lt=1).exclude(
                product__product_id=var).filter(
                reduce(operator.or_, (Q(
                    product__categories__icontains=x) for x in categories)))
            linked_sorted = linked_products.order_by('-stock_count')
            linked_sorted_distinct = linked_products.distinct('product_id')
            linked_distinct_flavour = linked_products.distinct(
                'product_id', 'flavour').order_by('product_id', 'flavour')
            linked_distinct_size = linked_products.distinct(
                'product_id', 'size').order_by('product_id', 'size')
            js_linked_sorted = json_serializer.serialize(linked_sorted.order_by(
                '-stock_count','product_id','flavour'), ensure_ascii=False)

            return render(request, 'product_page.html',
                          {'product': product,
                           'linked_sorted': linked_sorted,
                           'linked_sorted_distinct': linked_sorted_distinct,
                           'linked_distinct_flavour': linked_distinct_flavour,
                           'linked_distinct_size': linked_distinct_size,
                           'js_product': js_product,
                           'js_linked_sorted': js_linked_sorted})
        else:
            return render(request, 'product_page.html',
                          {'product': product,
                           'js_product': js_product})
    else:
        return render(request, 'product_page.html',
                      {'product': product,
                       'js_product': js_product})


def profile_vars(request):
    default_address = Addresses.objects.filter(
        user=request.user,
        default_addr=True)
    other_address = Addresses.objects.filter(
        user=request.user,
        default_addr=False).order_by('pk')
    orders = PurchaseHistory.objects.all().filter(
        purchaser=request.user).order_by('-order_dt')
    return default_address, other_address, orders


def delete_acc(request):
    User.delete(request.user)
    logout(request)
    messages.success(request, 'Account successfully deleted')


def default_addr(request):
    make_default = request.POST.get("mk-default-button")
    def_addr_req = Addresses.objects.filter(user=request.user,
                                            pk=make_default)
    default = Addresses.objects.filter(user=request.user,
                                       default_addr=True)
    if default:
        default.update(default_addr=False)
    def_addr_req.update(default_addr=True)
    messages.success(
        request,
        'You successfully updated your default address.')


def edit_addr(request):
    edit_addr_id = request.POST.get("edit-addr-button")
    return edit_addr_id


def delete_addr(request):
    del_addr_id = request.POST.get("del-addr-button")
    Addresses.objects.get(user=request.user,
                          pk=del_addr_id).delete()
    messages.success(
        request,
        'You successfully deleted your address ' +
        'from your account.')


def profile_view(request):
    if request.user.is_authenticated:
        default_address, other_address, orders = profile_vars(request)
        if request.method == 'POST':
            if request.POST.get("del-acc-button"):
                delete_acc(request)
                return redirect(homepage_view)
            if request.POST.get("mk-default-button"):
                default_addr(request)
                return redirect('addresses')
            if request.POST.get("edit-addr-button"):
                edit_addr_id = edit_addr(request)
                return redirect('edit-address', edit_addr_id)
            if request.POST.get("del-addr-button"):
                delete_addr(request)
                return redirect('addresses')
        else:
            return render(request, 'profile.html',
                          {'default_address': default_address,
                           'other_address': other_address,
                           'orders': orders})
    else:
        return render(request, 'profile.html')


def profile_addr(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            addr_form = AddressForm(request.POST)
            if addr_form.is_valid():
                if request.POST.get("save-addr-button"):
                    default = Addresses.objects.filter(user=request.user,
                                                       default_addr=True)
                    obj = addr_form.save(commit=False)
                    if default and obj.default_addr:
                        default.update(default_addr=False)
                    obj.user = request.user
                    obj.save()
                    messages.success(
                        request,
                        'You successfully added your address ' +
                        'to your account.')
                    return redirect('addresses')
        else:
            addr_form = AddressForm()
        return render(request, 'profile.html',
                      {'addr_form': addr_form})
    else:
        return render(request, 'profile.html')


def profile_edit_addr(request, var):
    if request.user.is_authenticated:
        addr_to_edit = Addresses.objects.filter(user=request.user,
                                                pk=var)
        if request.method == 'POST':
            edit_addr_form = AddressForm(request.POST,
                                         instance=addr_to_edit[0])
            if edit_addr_form.is_valid():
                if request.POST.get("save-edit-addr-button"):
                    default = Addresses.objects.filter(user=request.user,
                                                       default_addr=True)
                    obj = edit_addr_form.save(commit=False)
                    if default and obj.default_addr:
                        default.update(default_addr=False)
                    obj.save()
                    messages.success(
                        request,
                        'You successfully edited your address.')
                    return redirect('addresses')
        else:
            edit_addr_form = AddressForm()
        return render(request, 'profile.html',
                      {'edit_addr_form': edit_addr_form,
                       'addr_to_edit': addr_to_edit[0]})
    else:
        return render(request, 'profile.html')


def profile_orders(request, var):
    if request.user.is_authenticated:
        order = PurchaseHistory.objects.all().filter(
            purchaser=request.user,
            pk=var)
        if order:
            order_details = Purchases.objects.all().filter(
                order=order[0]).order_by('product__product_id')
            products = ProductDetails.objects.filter(
                product__product_id__in=order_details.values(
                    'product__product_id')).order_by('product_id')
            return render(request, 'profile.html',
                          {'order': order[0],
                           'order_details': zip(order_details, products)})
    return render(request, 'profile.html')


def all_products(request):
    products = ProductDetails.objects.all().exclude(active=False)
    products_distinct, js_products = product_pages(request, products)

    return render(request, 'all_products.html',
                  {'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def sports_products(request):
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__categories__icontains='sports')
    products_distinct, js_products = product_pages(request, products)

    return render(request, 'all_products.html',
                  {'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def health_products(request):
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__categories__icontains='health')
    products_distinct, js_products = product_pages(request, products)

    return render(request, 'all_products.html',
                  {'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def new_products(request):
    prv_mo = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=30)
    products = ProductDetails.objects.all().exclude(
        active=False).exclude(
        stock_count__lte=0).filter(created_ts__gte=prv_mo)
    products_distinct, js_products = product_pages(request, products)

    return render(request, 'all_products.html',
                  {'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def add_cart(request, product_id):
    flavour = request.POST.get(product_id + '-prod-flavours')
    size = request.POST.get(product_id + '-prod-sizes')
    quantity = int(request.POST.get(product_id + '-prod-quantity'))

    if flavour:
        details_pk = str(ProductDetails.objects.filter(
            product__product_id=product_id).filter(
            flavour=flavour).filter(size=size)[0].pk)
    else:
        details_pk = str(ProductDetails.objects.filter(
            product__product_id=product_id).filter(
            size=size)[0].pk)

    redirect_url = request.POST.get('redirect_url')
    cart = request.session.get('cart', {})

    if details_pk in list(cart.keys()):
        cart[details_pk] += quantity
    else:
        cart[details_pk] = quantity

    request.session['cart'] = cart
    return redirect(redirect_url)


def cart_view(request):
    try:
        cart = request.session['cart']
    except KeyError:
        cart = request.session.get('cart', {})

    if cart:
        cart_prods = list()
        total = 0

        for product in cart:
            prod_details = ProductDetails.objects.filter(pk=product)[0]
            cart_prods.append(prod_details)
            total += prod_details.price * cart[product]

        if total < settings.FREE_SHIPPING_THRESHOLD:
            shipping = round(total * Decimal(settings.STANDARD_SHIPPING_PERCENTAGE)/100, 2)
        else:
            shipping = 0

        grand_total = shipping + total

        return render(request, 'cart.html',
                      {'cart_prods': zip(cart_prods, cart.values()),
                       'total': total,
                       'shipping': shipping,
                       'grand_total': grand_total})

    else:
        return render(request, 'cart.html')


def update_cart(request):
    try:
        cart = request.session['cart']
    except KeyError:
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
                        loop_count += 1
                        if loop_count == 1:
                            messages.success(
                                request, 'You successfully updated your cart')
        elif '-prod-del' in i:
            details_pk = i.split('-prod-del')[0]
            del cart[details_pk]
            loop_count += 1
            if loop_count == 1:
                messages.success(
                    request, 'You successfully removed the item from your cart')
        request.session['cart'] = cart

    if request.POST.get("empty-cart-button"):
        del request.session['cart']
        messages.success(
            request, 'You successfully emptied your cart')

    redirect_url = request.POST.get('redirect_url')
    return redirect(redirect_url)
