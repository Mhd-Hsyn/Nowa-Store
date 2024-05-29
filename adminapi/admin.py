from django.contrib import admin
from .models import *


admin.site.register([AdminAuth,AdminWhitelistToken, ProductCategory, Brand, Product])
