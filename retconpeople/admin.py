from django.contrib import admin
from .models import UserName,UserNumber,Person,Website

# Register your models here.


class UserNameInline(admin.TabularInline):
    model = UserName

class UserNumberInline(admin.TabularInline):
    model = UserNumber

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [
        UserNameInline,UserNumberInline
    ]

    pass

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):

    pass

    

@admin.register(UserName)
class UserNameAdmin(admin.ModelAdmin):

    pass

@admin.register(UserNumber)
class UserNumberAdmin(admin.ModelAdmin):

    pass