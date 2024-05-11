from allauth.account.views import PasswordChangeView, EmailView, \
    ConfirmEmailView, EmailVerificationSentView
from django.urls import reverse_lazy
from .models import *
from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView
from django.contrib import messages
from django.contrib.auth import logout
from .forms import *


def homepage_view(request):
    products = Products.objects.all().exclude(active=False)
    new_product = Products.objects.all().filter(
        stock_count__gte=10).latest('created_ts')
    sports_product = Products.objects.all().filter(
        categories__icontains='sports').order_by('-stock_count').first()
    health_product = Products.objects.all().filter(
        categories__icontains='health').order_by('-stock_count').first()

    if new_product == sports_product:
        sports_product = Products.objects.all().filter(
            categories__icontains='sports').order_by('-stock_count')[1]
    if new_product == health_product:
        health_product = Products.objects.all().filter(
            categories__icontains='health').order_by('-stock_count')[1]

    return render(request, 'index.html',
                  {'products': products,
                   'new_product': new_product,
                   'sports_product': sports_product,
                   'health_product': health_product})


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


def profile_view(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if request.POST.get("delete-button"):
                User.delete(request.user)
                logout(request)
                messages.success(request, 'Account successfully deleted')
                return redirect(homepage_view)
        else:
            return render(request, 'profile.html')
    else:
        return render(request, 'profile.html')