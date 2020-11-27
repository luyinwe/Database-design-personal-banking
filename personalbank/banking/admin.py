from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(operator)
admin.site.register(user)
admin.site.register(account)
admin.site.register(loan)
admin.site.register(wire_transfer)
admin.site.register(transaction)