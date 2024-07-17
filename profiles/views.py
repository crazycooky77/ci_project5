from uuid import UUID
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from addresses.views import default_addr, edit_addr, delete_addr, get_addresses
from checkout.models import OrderHistory
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


def newsletter_signup(request):
    def _send_signup_email(cust_email, link):
        subject = render_to_string(
            'confirmation_emails/newsletter-signup-subject.txt')
        body = render_to_string(
            'confirmation_emails/newsletter-signup-body.txt',
            {'link': link})
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [cust_email])

    if request.method == 'POST':
        if request.POST.get('news-email-button'):
            redirect_url = request.POST.get('redirect_url')
            news_email = request.POST.get('news_email')
            newsletter_form = NewsletterForm(
                {'news_email': news_email})
            signed_up = Newsletter.objects.filter(news_email__iexact=news_email)
            if newsletter_form.is_valid() and not signed_up:
                obj = newsletter_form.save(commit=False)
                obj.save()
                unsub_link = request.META['HTTP_ORIGIN'] + '/unsub=' + obj.news_uuid
                _send_signup_email(news_email, unsub_link)
                messages.success(
                    request, 'Thank you for signing up to our newsletter!')
            elif signed_up:
                messages.success(
                    request, "Good news, you're already signed up!")
            else:
                messages.error(
                    request, "Please enter a valid email address")
            if '/unsub=' in redirect_url:
                return redirect('/')
            else:
                return redirect(redirect_url)


def unsubscribe_view(request, var):
    if var:
        try:
            uuid_var = UUID(var, version=4)
        except ValueError:
            uuid_var = None

        if uuid_var:
            signed_up = Newsletter.objects.filter(news_uuid=var)
            if signed_up:
                signed_up.delete()
                unsub = True
                return render(request, 'unsubscribe.html',
                              {'unsub': unsub})
            else:
                return render(request, 'unsubscribe.html',
                              {'valid_uuid': True})
        else:
            return render(request, 'unsubscribe.html',
                          {'invalid_uuid': True})
    else:
        return render(request, 'unsubscribe.html')


def profile_vars(request):
    default_address, other_address = get_addresses(request)
    orders = OrderHistory.objects.filter(
        purchaser=request.user).order_by('-order_dt')
    signed_up = Newsletter.objects.filter(news_email__iexact=request.user.email)
    return default_address, other_address, orders, signed_up


def unsub_news(request, signed_up):
    signed_up.delete()
    messages.success(request,
                     'You successfully unsubscribed from our newsletter')


def delete_acc(request, signed_up):
    signed_up.delete()
    User.delete(request.user)
    logout(request)
    messages.success(request, 'Account successfully deleted')


def profile_view(request):
    if request.user.is_authenticated:
        default_address, other_address, orders, signed_up \
            = profile_vars(request)
        if request.method == 'POST':
            if request.POST.get('unsub-news-button'):
                unsub_news(request, signed_up)
                return redirect('profile')
            if request.POST.get("del-acc-button"):
                delete_acc(request, signed_up)
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
                           'orders': orders,
                           'signed_up': signed_up})
    else:
        return render(request, 'profile.html')
