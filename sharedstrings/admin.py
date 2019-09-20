from django.contrib import admin
from .models import Strings

@admin.register(Strings)
class SharedStringAdmin(admin.ModelAdmin):
    search_fields = ['name']
# Register your models here.

