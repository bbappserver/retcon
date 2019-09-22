from django.contrib import admin
from .models import UserName,UserNumber,Person,Website

# Register your models here.


class UserNameInline(admin.TabularInline):
    autocomplete_fields=["name","website"]
    exclude=["tags"]
    model = UserName

class UserNumberInline(admin.TabularInline):
    model = UserNumber
    autocomplete_fields=["website"]

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    autocomplete_fields=["pseudonyms","tags","first_name","last_name"]
    inlines = [
        UserNameInline,UserNumberInline
    ]

    pass

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    search_fields=["domain"]
    pass

    

@admin.register(UserName)
class UserNameAdmin(admin.ModelAdmin):
    search_fields=["name"]
    autocomplete_fields=["tags","name","website"]
    pass

@admin.register(UserNumber)
class UserNumberAdmin(admin.ModelAdmin):

    pass