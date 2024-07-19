from django.contrib import admin
from .models import *


# Admin site registration for User model
admin.site.register([User])
