from django.contrib import admin
from django.db.models import Q
from .models import UserName,UserNumber,Person,Website

# Register your models here.

def merge_people(modeladmin, request, queryset):
    # queryset.update(status='p')
    pass
merge_people.short_description = "Combine aliased people into the oldest one."


class UserNameInline(admin.TabularInline):
    autocomplete_fields=["name","website"]
    exclude=["tags"]
    model = UserName

class UserNumberInline(admin.TabularInline):
    model = UserNumber
    autocomplete_fields=["website"]

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    search_fields=['first_name','last_name','pseudonyms']
    autocomplete_fields=["pseudonyms","tags","first_name","last_name","merged_into"]
    inlines = [
        UserNameInline,UserNumberInline
    ]
    order_by=('last_name','first_name')

    def get_search_results(self, request, queryset, search_term):
        q=Q(first_name__name__istartswith=search_term) | Q(last_name__name__istartswith=search_term)
        q1=Person.objects.filter(q)
        q2=Person.objects.filter(pseudonyms__name__istartswith=search_term)
        q3=Person.objects.filter(usernames__name__name__istartswith=search_term)
        return (q1 | q2 |q3 ,True)
        # return super().get_search_results(request, queryset, search_term)

    pass

@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    search_fields=["domain"]
    autocomplete_fields=["tld","tags","name","parent_site"]
    pass

    

@admin.register(UserName)
class UserNameAdmin(admin.ModelAdmin):
    search_fields=["name"]
    autocomplete_fields=["tags","name","website"]
    pass

@admin.register(UserNumber)
class UserNumberAdmin(admin.ModelAdmin):

    pass