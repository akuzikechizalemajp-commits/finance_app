from django.contrib import admin

# Register your models here.
from .models import Budget, Income, Expense

admin.site.register(Income)
admin.site.register(Expense)
admin.site.register(Budget)

