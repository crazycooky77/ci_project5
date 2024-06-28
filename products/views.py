from django.db.models.functions import Lower
from django.shortcuts import render
from .models import *
from django.db.models import Q
from django.db.models import Case, When
from django.core import serializers
import operator
from functools import reduce
import pytz
import datetime


def product_sort(request, data, active_sort, *args):
    sale_flag = False
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
            on_sale=True).values_list(
            'id', flat=True)
        sale_flag = True
    else:
        try:
            del request.session['active_sort']
            active_sort = None
        except KeyError:
            active_sort = None

        sorted_data = data.order_by(
            '-stock_count').values_list(
            'product__product_id', flat=True)

    if args:
        search_term = args[0]
        sorted_data = data.filter(
            flavour__icontains=search_term).values_list(
            'id', flat=True)
        js_products = json_sorted_serialise(sorted_data, search_term)
    else:
        js_products = json_sorted_serialise(sorted_data)

    sorted_data = list(dict.fromkeys(sorted_data))
    return [sorted_data, js_products, active_sort, sale_flag]


def json_sorted_serialise(sorted_data, *args):
    if sorted_data:
        preserved_list = Case(
            *[When(pk=pk, then=pos) for pos, pk in enumerate(sorted_data)])
        if args:
            qs = ProductDetails.objects.all().exclude(active=False).filter(
                pk__in=sorted_data).order_by(preserved_list)
        else:
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


def json_serialise(data, *args):
    json_serializer = serializers.get_serializer("json")()

    if args:
        list_args = [a for a in args]
        js_products = json_serializer.serialize(
            data.order_by(*list_args, 'flavour', 'size'),
            ensure_ascii=False,
            fields=('pk', 'size', 'size_unit',
                    'flavour', 'price',
                    'stock_count',
                    'product')
        )
    else:
        js_products = json_serializer.serialize(
            data.order_by('flavour', 'size'),
            ensure_ascii=False,
            fields=('pk', 'size', 'size_unit',
                    'flavour', 'price',
                    'stock_count',
                    'product')
        )
    return js_products


def product_pages(request, qs, active_sort, *args):
    if args:
        search_term = args[0]
        products_sorted, js_products, active_sort, sale_flag = product_sort(
            request, qs, active_sort, search_term)
    else:
        products_sorted, js_products, active_sort, sale_flag = product_sort(
            request, qs, active_sort)

    if args or sale_flag:
        product_list = ProductDetails.objects.filter(
            pk__in=products_sorted).distinct(
            'product__product_id')
        products_distinct = list()
        for product_id in products_sorted:
            products_distinct.append(product_list.get(pk=product_id))
    else:
        product_list = ProductDetails.objects.filter(
            product__product_id__in=products_sorted).distinct(
            'product__product_id')
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
        product_searched = ProductDetails.objects.all().exclude(
            active=False).filter(pk__in=flavour_searched)
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

    if ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0).filter(stock_count__gte=10):
        new_product = ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0).filter(
            stock_count__gte=10).latest('created_ts')
    elif ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0):
        new_product = ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0).latest(
            'created_ts')
    else:
        new_product = ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0)
    sports_product = ProductDetails.objects.all().exclude(
        active=False).exclude(pk=0).filter(
        product__main_cat='SPORTS').order_by(
        '-stock_count').first()
    health_product = ProductDetails.objects.all().exclude(
        active=False).exclude(pk=0).filter(
        product__main_cat='HEALTH').order_by(
        '-stock_count').first()

    if new_product:
        new_product_extras = ProductDetails.objects.all().exclude(
            active=False).filter(
            product__product_id=new_product.product_id)
        js_new_product = json_serialise(new_product_extras)
    else:
        new_product_extras = ''
        js_new_product = ''

    if sports_product:
        sports_product_extras = ProductDetails.objects.all().exclude(
            active=False).filter(
            product__product_id=sports_product.product_id)
        js_sports_product = json_serialise(sports_product_extras)
    else:
        sports_product_extras = ''
        js_sports_product = ''
    if health_product:
        health_product_extras = ProductDetails.objects.all().exclude(
            active=False).filter(
            product__product_id=health_product.product_id)
        js_health_product = json_serialise(health_product_extras)
    else:
        health_product_extras = ''
        js_health_product = ''

    if (new_product == sports_product
            and new_product != ''
            and sports_product != ''):
        all_sports = ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0).filter(
            product__main_cat='SPORTS').order_by(
            '-stock_count')
        if all_sports.count() > 1:
            sports_product = all_sports[1]
            sports_product_extras = ProductDetails.objects.all().exclude(
                active=False).filter(
                product__product_id=sports_product.product_id)
        else:
            sports_product = ProductDetails.objects.none()
            sports_product_extras = ProductDetails.objects.none()
    if (new_product == health_product
            and new_product != ''
            and health_product != ''):
        all_health = ProductDetails.objects.all().exclude(
            active=False).exclude(pk=0).filter(
            product__main_cat='HEALTH').order_by(
            '-stock_count')
        if all_health.count() > 1:
            health_product = all_health[1]
            health_product_extras = ProductDetails.objects.all().exclude(
                active=False).filter(
                product__product_id=health_product.product_id)
        else:
            health_product = ProductDetails.objects.none()
            health_product_extras = ProductDetails.objects.none()

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


def product_view(request, var):
    product = ProductDetails.objects.all().exclude(active=False).filter(
        product__product_id=var)
    js_product = json_serialise(product)
    product_cats = Products.objects.all().filter(product_id=var)

    if product_cats:
        categories = product_cats[0].categories.split(',')
        categories = [cat.strip(' ') for cat in categories]
        for cat in categories:
            cat.strip()

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
            js_linked_sorted = json_serialise(linked_sorted, '-stock_count', 'product_id')

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


def all_products(request):
    active_sort = get_active_sort(request)
    products = ProductDetails.objects.all().exclude(active=False)
    products_distinct, js_products, active_sort = product_pages(
        request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def sports_products(request):
    active_sort = get_active_sort(request)
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__main_cat='SPORTS')
    products_distinct, js_products, active_sort = product_pages(
        request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def health_products(request):
    active_sort = get_active_sort(request)
    products = ProductDetails.objects.all().exclude(active=False).filter(
        product__main_cat='HEALTH')
    products_distinct, js_products, active_sort = product_pages(
        request, products, active_sort)
    del_active_sort(request)

    return render(request, 'all_products.html',
                  {'active_sort': active_sort,
                   'products': products,
                   'products_distinct': products_distinct,
                   'js_products': js_products})


def new_products(request):
    active_sort = get_active_sort(request)
    prv_mo = datetime.datetime.now(pytz.UTC) - datetime.timedelta(days=30)
    products_init = ProductDetails.objects.all().exclude(
        active=False).exclude(
        stock_count__lte=0).filter(created_ts__gte=prv_mo)
    products = ProductDetails.objects.all().filter(
        product__product_id__in=products_init.values_list(
            'product_id', flat=True))
    products_distinct, js_products, active_sort = product_pages(
        request, products, active_sort)
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

        products_distinct, js_products, active_sort = product_pages(
            request, products, active_sort)

        if search_term:
            product_searched, js_searched, searched_sort = product_pages(
                request, product_searched, active_sort, search_term)
        else:
            product_searched, js_searched, searched_sort = product_pages(
                request, product_searched, active_sort)

        del_active_sort(request)

        return render(request, 'all_products.html',
                      {'active_sort': active_sort,
                       'search_term': search_term,
                       'sort_search': sort_search,
                       'products': products,
                       'products_distinct': products_distinct,
                       'js_products': js_products,
                       'js_searched': js_searched})

    else:
        search_term = None
        sort_search = None
        products = ProductDetails.objects.none()
        products_distinct = ProductDetails.objects.none()
        js_products = None
        js_searched = None

        return render(request, 'all_products.html',
                      {'active_sort': active_sort,
                       'search_term': search_term,
                       'sort_search': sort_search,
                       'products': products,
                       'products_distinct': products_distinct,
                       'js_products': js_products,
                       'js_searched': js_searched})
