from django.contrib import admin
from .models import *


# Admin site models
admin.site.register([User,
                     Addresses,
                     Products,
                     PurchaseHistory,
                     Purchases,
                     SavedItems])