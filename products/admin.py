from django.contrib import admin
from .models import Category,Products

# Register your models here.

admin.site.register(Products)
admin.site.register(Category)
