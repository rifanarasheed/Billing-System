from django.contrib import admin
from .models import Order,OrderLines,Product,Purchase

# Register your models here.
admin.site.register(Product)
admin.site.register(Purchase)
