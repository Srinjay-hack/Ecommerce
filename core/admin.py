from django.contrib import admin
from .models import Items,OrderItems,Order
# Register your models here.

admin.site.register(Items)
admin.site.register(OrderItems)
admin.site.register(Order)
