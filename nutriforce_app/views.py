from .models import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from .forms import *


def homepage_view(request):
    return render(request, 'index.html')