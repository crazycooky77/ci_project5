from django.contrib import admin
from .models import *


# Admin site registration for OrderHistory and Purchases models
admin.site.register([OrderHistory,
                     Purchases])
