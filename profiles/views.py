from .models import *
from allauth.account.views import PasswordChangeView, EmailView, \
    ConfirmEmailView, EmailVerificationSentView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import render, redirect
from products.views import homepage_view
from .forms import *


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


def profile_vars(request):
    default_address = Addresses.objects.filter(
        user=request.user,
        default_addr=True)
    other_address = Addresses.objects.filter(
        user=request.user,
        default_addr=False).order_by('pk')
    orders = OrderHistory.objects.all().filter(
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
            updated_request = request.POST.copy()
            updated_request.update({'country': 'IE'})
            addr_form = AddressForm(updated_request)
            if request.POST.get("save-addr-button"):
                if addr_form.is_valid():
                    default = Addresses.objects.filter(user=request.user,
                                                       default_addr=True)
                    obj = addr_form.save(commit=False)
                    if default and obj.default_addr:
                        default.update(default_addr=False)
                    obj.user = request.user
                    obj.email = request.user.email
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
        order = OrderHistory.objects.all().filter(
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
