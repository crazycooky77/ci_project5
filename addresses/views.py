from django.shortcuts import render, redirect
from django.db.models import Q
from checkout.models import OrderHistory
from .models import Addresses
from django.contrib import messages
from .forms import AddressForm


def get_addresses(request):
    default_address = Addresses.objects.filter(
        user=request.user,
        default_addr=True)
    other_address = Addresses.objects.filter(
        user=request.user,
        default_addr=False).order_by('pk')
    return default_address, other_address


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
    orders = OrderHistory.objects.filter(Q(
        shipping_addr=del_addr_id) | Q(billing_addr=del_addr_id))
    if orders:
        Addresses.objects.filter(user=request.user,
                                 pk=del_addr_id).update(user=None)
        messages.success(
            request,
            'You successfully removed your address ' +
            'from your account. It remains in our system, as ' +
            'you had an order associated with it. Please contact ' +
            'our support, if you want the address deleted completely.')
    else:
        Addresses.objects.get(user=request.user,
                              pk=del_addr_id).delete()
        messages.success(
            request,
            'You successfully deleted your address ' +
            'from your account.')


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
            updated_request = request.POST.copy()
            updated_request.update({'country': 'IE'})
            edit_addr_form = AddressForm(updated_request,
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
