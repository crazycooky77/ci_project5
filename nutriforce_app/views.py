import json
from decimal import Decimal
import pytz
from django.core import serializers
from allauth.account.views import PasswordChangeView, EmailView, \
    ConfirmEmailView, EmailVerificationSentView
from django.contrib.auth.signals import user_logged_in
from django.db.models import Case, When
from django.dispatch import receiver
from django.urls import reverse_lazy
from nutriforce import settings
from .models import *
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth import logout
import operator
import datetime
from django.db.models import Q, F
from django.db.models.functions import Lower
from functools import reduce
from .forms import *


@receiver(user_logged_in)
def cart_merge(sender, user, request, **kwargs):
    try:
        cart = request.session['cart']
    except KeyError:
        cart = request.session.get('cart', {})

    if request.user.is_authenticated:
        user_cart = SavedItems.objects.filter(
            owner=request.user,
            list_type='CART').values_list(
            'product__product_id', 'quantity')
        user_cart_ids_set = set()
        user_cart_quantity = list()
        cart_ids_set = set()

        for prod_id, quantity in user_cart:
            user_cart_ids_set.add(str(prod_id))
            user_cart_quantity.append(quantity)

        for prod_id in cart:
            cart_ids_set.add(str(prod_id))

        for prod in cart:
            if str(prod) not in user_cart_ids_set.intersection(cart_ids_set):
                user_cart, created = SavedItems.objects.get_or_create(
                    owner=request.user,
                    list_type='CART',
                    product=ProductDetails.objects.get(pk=prod),
                    defaults={'quantity': cart[prod]})
                if created:
                    user_cart.quantity = F('quantity') + cart[prod]

        updated_cart = SavedItems.objects.filter(owner=request.user,
                                                 list_type='CART').values()
        cart = {}
        for prod in updated_cart:
            cart[str(prod['product_id'])] = prod['quantity']
        request.session['cart'] = cart

        return cart

    else:
        return cart


def product_sort(request, data, active_sort):
    if request.POST.get('brand-asc') or active_sort == 'brand-asc':
        active_sort = 'brand-asc'
        request.session['active_sort'] = active_sort
        sorted_data = data.order_by(
            Lower('product__brand')).values_list(
            'product__product_id', flat=True)
    elif request.POST.get('brand-desc') or active_sort == 'brand-desc':
        active_sort = 'brand-desc'
        request.session['active_sort'] = active_sort
        sorted_data = data.order_by(
            Lower('product__brand').desc()).values_list(
            'product__product_id', flat=True)
    elif request.POST.get('prod-asc') or active_sort == 'prod-asc':
        active_sort = 'prod-asc'
        request.session['active_sort'] = active_sort
        sorted_data = data.order_by(
            Lower('product__product_name')).values_list(
            'product__product_id', flat=True)
    elif request.POST.get('prod-desc') or active_sort == 'prod-desc':
        active_sort = 'prod-desc'
        request.session['active_sort'] = active_sort
        sorted_data = data.order_by(
            Lower('product__product_name').desc()).values_list(
            'product__product_id', flat=True)
    elif request.POST.get('price-asc') or active_sort == 'price-asc':
        active_sort = 'price-asc'
        request.session['active_sort'] = active_sort
        sorted_data = data.order_by(
            'price').values_list(
            'product__product_id', flat=True)
    elif request.POST.get('price-desc') or active_sort == 'price-desc':
        active_sort = 'price-desc'
        request.session['active_sort'] = active_sort
        sorted_data = data.order_by(
            '-price').values_list(
            'product__product_id', flat=True)
    elif request.POST.get('sale') or active_sort == 'sale':
        active_sort = 'sale'
        request.session['active_sort'] = active_sort
        sorted_data = data.filter(
            product__categories__icontains='sale').values_list(
            'product__product_id', flat=True)
    else:
        try:
            del request.session['active_sort']
            active_sort = None
        except KeyError:
            active_sort = None

        sorted_data = data.order_by(
            '-stock_count').values_list(
            'product__product_id', flat=True)

    js_products = json_serialise(sorted_data)
    sorted_data = list(dict.fromkeys(sorted_data))
    return [sorted_data, js_products, active_sort]


def json_serialise(sorted_data):
    if sorted_data:
        preserved_list = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_data)])
        qs = ProductDetails.objects.all().exclude(active=False).filter(
            product__product_id__in=sorted_data).order_by(preserved_list)

    else:
        qs = ProductDetails.objects.none()

    js_products = serializers.serialize('json', qs,
                                        ensure_ascii=False,
                                        fields=('pk', 'size', 'size_unit',
                                                'flavour', 'price',
                                                'stock_count',
                                                'product'))

    return js_products


def product_pages(request, qs, active_sort):
    products_sorted, js_products, active_sort = product_sort(request, qs, active_sort)
    product_list = ProductDetails.objects.filter(
        product_id__in=products_sorted).distinct('product_id')
    products_distinct = list()
    for product_id in products_sorted:
        products_distinct.append(product_list.get(product_id=product_id))

    return products_distinct, js_products, active_sort


def search_sort(request, term):
    product_filter = ProductDetails.objects.all().exclude(
        active=False).filter(
        Q(flavour__icontains=term) |
        Q(product__brand__icontains=term) |
        Q(product__product_name__icontains=term))
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__product_id__in=product_filter.values_list(
            'product__product_id',
            flat=True))

    flavour_searched = []
    for prod in product_filter:
        if prod.flavour:
            if prod.flavour.lower() == term.lower():
                if prod.pk not in flavour_searched:
                    flavour_searched.append(prod.pk)

    if flavour_searched:
        product_searched = ProductDetails.objects.all().exclude(active=False).filter(
            pk__in=flavour_searched)
    else:
        product_searched = ProductDetails.objects.none()

    return [products, product_searched]


def get_active_sort(request):
    active_sort = request.POST.get('active_sort')
    if active_sort:
        request.session['active_sort'] = active_sort
    else:
        try:
            active_sort = request.session['active_sort']
        except KeyError:
            request.session['active_sort'] = None
            active_sort = None

    return active_sort


def del_active_sort(request):
    try:
        del request.session['active_sort']
    except KeyError:
        pass


def homepage_view(request):
    products = ProductDetails.objects.all().exclude(active=False)
    json_serializer = serializers.get_serializer("json")()

    if ProductDetails.objects.all().exclude(active=False).exclude(pk=0).filter(stock_count__gte=10):
        new_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0).filter(
            stock_count__gte=10).latest('created_ts')
    elif ProductDetails.objects.all().exclude(active=False).exclude(pk=0):
        new_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0).latest(
            'created_ts')
    else:
        new_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0)
    sports_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0).filter(
        product__categories__icontains='sports').order_by(
        '-stock_count').first()
    health_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0).filter(
        product__categories__icontains='health').order_by(
        '-stock_count').first()

    if new_product:
        new_product_extras = ProductDetails.objects.all().exclude(active=False).filter(
            product__product_id=new_product.product_id)
        js_new_product = json_serializer.serialize(
            new_product_extras.order_by('flavour'),
            ensure_ascii=False)
    else:
        new_product_extras = ''
        js_new_product = ''

    if sports_product:
        sports_product_extras = ProductDetails.objects.all().exclude(active=False).filter(
            product__product_id=sports_product.product_id)
        js_sports_product = json_serializer.serialize(
            sports_product_extras.order_by('flavour'),
            ensure_ascii=False)
    else:
        sports_product_extras = ''
        js_sports_product = ''
    if health_product:
        health_product_extras = ProductDetails.objects.all().exclude(active=False).filter(
            product__product_id=health_product.product_id)
        js_health_product = json_serializer.serialize(
            health_product_extras.order_by('flavour'),
            ensure_ascii=False)
    else:
        health_product_extras = ''
        js_health_product = ''

    if new_product == sports_product and new_product != '' and sports_product != '':
        sports_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0).filter(
            product__categories__icontains='sports').order_by(
            '-stock_count')[1]
        sports_product_extras = ProductDetails.objects.all().exclude(active=False).filter(
            product__product_id=sports_product.product_id)
    if new_product == health_product and new_product != '' and health_product != '':
        health_product = ProductDetails.objects.all().exclude(active=False).exclude(pk=0).filter(
            product__categories__icontains='health').order_by(
            '-stock_count')[1]
        health_product_extras = ProductDetails.objects.all().exclude(active=False).filter(
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
    active_sort = get_active_sort(request)
    products = ProductDetails.objects.all().exclude(active=False)
    products_distinct, js_products, active_sort = product_pages(request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def sports_products(request):
    active_sort = get_active_sort(request)
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__categories__icontains='sports')
    products_distinct, js_products, active_sort = product_pages(request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def health_products(request):
    active_sort = get_active_sort(request)
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__categories__icontains='health')
    products_distinct, js_products, active_sort = product_pages(request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def new_products(request):
    active_sort = get_active_sort(request)
    prv_mo = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=30)
    products = ProductDetails.objects.all().exclude(
        active=False).exclude(
        stock_count__lte=0).filter(created_ts__gte=prv_mo)
    products_distinct, js_products, active_sort = product_pages(request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def search_results(request):
    active_sort = get_active_sort(request)
    if request.method == 'POST':
        search_term = request.POST.get('nav-search')
        sort_search = request.POST.get('sort-search')

        if search_term:
            products, product_searched = search_sort(request, search_term)
        elif sort_search:
            products, product_searched = search_sort(request, sort_search)
            search_term = sort_search
        else:
            search_term = None
            product_searched = ProductDetails.objects.none()
            products = ProductDetails.objects.none()

        products_distinct, js_products, active_sort = product_pages(request, products, active_sort)
        product_searched, js_searched, searched_sort = product_pages(request, product_searched, active_sort)
        del_active_sort(request)

        return render(request, 'all_products.html',
                      {'active_sort': active_sort,
                       'search_term': search_term,
                       'sort_search': sort_search,
                       'products': products,
                       'products_distinct': products_distinct,
                       'js_products': js_products,
                       'js_searched': js_searched})


def add_cart(request, product_id):
    request.session['active_sort'] = request.POST.get('active_sort')

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

    if request.user.is_authenticated:
        user_cart, created = SavedItems.objects.get_or_create(
            owner=request.user,
            list_type='CART',
            product=ProductDetails.objects.get(pk=int(details_pk)),
            defaults={'quantity': quantity})
        if not created:
            user_cart.quantity = F('quantity') + quantity
        user_cart.save()
        if quantity > 1:
            messages.success(
                request,
                f'You successfully added {quantity} items to your cart.')
        else:
            messages.success(
                request,
                f'You successfully added {quantity} item to your cart.')

        updated_cart = SavedItems.objects.filter(owner=request.user,
                                                 list_type='CART').values()
        cart = {}
        for prod in updated_cart:
            cart[str(prod['product_id'])] = prod['quantity']

    else:
        cart = request.session.get('cart', {})

        if details_pk in list(cart.keys()):
            cart[details_pk] += quantity
        else:
            cart[details_pk] = quantity
        if quantity > 1:
            messages.success(
                request,
                f'You successfully added {quantity} items to your cart.')
        else:
            messages.success(
                request,
                f'You successfully added {quantity} item to your cart.')

    request.session['cart'] = cart
    redirect_url = request.POST.get('redirect_url')
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
