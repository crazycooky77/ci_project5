from django.shortcuts import render, redirect
from django.db.models import Q
from checkout.models import OrderHistory
from .models import Addresses
from django.contrib import messages
from .forms import AddressForm


def get_addresses(request):
    """Get saved addresses for logged-in user"""
    default_address = Addresses.objects.filter(
        user=request.user,
        default_addr=True)
    other_address = Addresses.objects.filter(
        user=request.user,
        default_addr=False).order_by('pk')
    return default_address, other_address


def default_addr(request):
    """Function for users to make a saved address their default"""
    make_default = request.POST.get('mk-default-button')
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
    """Get the address_id for the address the user wants to edit"""
    edit_addr_id = request.POST.get('edit-addr-button')
    return edit_addr_id


def delete_addr(request):
    """Function for users to delete a saved address from their account"""
    del_addr_id = request.POST.get('del-addr-button')
    orders = OrderHistory.objects.filter(Q(
        shipping_addr=del_addr_id) | Q(billing_addr=del_addr_id))
    # If address is linked to an order, only the reference to user is deleted
    if orders:
        Addresses.objects.filter(user=request.user,
                                 pk=del_addr_id).update(user=None)
        messages.success(
            request,
            'You successfully removed your address ' +
            'from your account. It remains in our system, as ' +
            'you had an order associated with it. Please contact ' +
            'our support, if you want the address deleted completely.')
    # Address deleted from database if no order is linked
    else:
        Addresses.objects.get(user=request.user,
                              pk=del_addr_id).delete()
        messages.success(
            request,
            'You successfully deleted your address ' +
            'from your account.')


def profile_add_addr(request):
    """View for users to add an address to their account
    (and the Addresses model)"""
    if request.user.is_authenticated:
        if request.method == 'POST':
            updated_request = request.POST.copy()
            updated_request.update({'country': 'IE'})
            addr_form = AddressForm(updated_request)
            if request.POST.get('save-addr-button'):
                if addr_form.is_valid():
                    default = Addresses.objects.filter(user=request.user,
                                                       default_addr=True)
                    obj = addr_form.save(commit=False)
                    # If default address exists and new address is also default
                    if default and obj.default_addr:
                        # Set default_addr to false for the old saved address
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
    """View for users to edit an address saved to their account"""
    if request.user.is_authenticated:
        addr_to_edit = Addresses.objects.filter(user=request.user,
                                                pk=var)
        if request.method == 'POST':
            updated_request = request.POST.copy()
            updated_request.update({'country': 'IE'})
            edit_addr_form = AddressForm(updated_request,
                                         instance=addr_to_edit[0])
            if edit_addr_form.is_valid():
                if request.POST.get('save-edit-addr-button'):
                    default = Addresses.objects.filter(user=request.user,
                                                       default_addr=True)
                    obj = edit_addr_form.save(commit=False)
                    # If default_addr exists and edited address is also default
                    if default and obj.default_addr:
                        # Set default_addr to false for other saved address
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
