from django.contrib import admin
from .models import Strings,Language

@admin.register(Strings)
class SharedStringAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    search_fields = ['name__istartswith','name_local__istartswith','isocode__exact']
# Register your models here.

