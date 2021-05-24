from django.contrib import admin
from django import forms
from django.db.models import Q
from .models import UserName,UserNumber,Person,Website,UrlPattern
# Register your models here.

def merge_people(modeladmin, request, queryset):
    # queryset.update(status='p')
    pass
merge_people.short_description = "Combine aliased people into the oldest one."

class ExternalPersonContentInline(admin.TabularInline):
    model=Person.external_representations.through
    extra=1
    verbose_name="External URL"
    verbose_name_plural="External URLs"
    autocomplete_fields=["contentresource"]

class UserNameInline(admin.TabularInline):
    autocomplete_fields=["name","website"]
    exclude=["tags"]
    model = UserName

class UserNumberInline(admin.TabularInline):
    model = UserNumber
    autocomplete_fields=["website"]

class UrlPatternInline(admin.TabularInline):
    model = UrlPattern


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    exclude=("external_representations",)
    search_fields=['first_name','last_name','pseudonyms']
    list_display=["id",'formatted_name','pseudonyms_readonly','first_name','last_name',"description","wanted_id_count"]
    list_filter=[]
    autocomplete_fields=["pseudonyms","tags","ambiguous_tags","first_name","last_name","distinguish_from"]
    raw_id_fields=('merged_into',)
    readonly_fields = ('uuid',)
    
    inlines = [
        UserNameInline,UserNumberInline,ExternalPersonContentInline
    ]
    order_by=('last_name','first_name')
    description = forms.CharField( widget=forms.Textarea )

    def get_search_results(self, request, queryset, search_term):
        if search_term == '':
            return (Person.objects.all(),True)
        try:
            id=int(search_term)
            q=Q(id=id)|Q(pseudonyms__name__icontains=search_term)|Q(usernames__name__name__istartswith=search_term)|Q(user_numbers__number=search_term)
            return (Person.objects.filter(q),True)
        except:
            pass
        q=Q(first_name__name__istartswith=search_term) | Q(last_name__name__istartswith=search_term)
        q1=Person.objects.filter(q)
        q2=Person.objects.filter(pseudonyms__name__icontains=search_term)

        if len(search_term)<3:
            q3=Person.objects.filter(usernames__name__name__istartswith=search_term)
        else:
            q3=Person.objects.filter(usernames__name__name__icontains=search_term)
        return (q1 | q2 |q3 ,True)
        # return super().get_search_results(request, queryset, search_term)


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    search_fields=["domain"]
    autocomplete_fields=["tld","tags","name","parent_site"]
    list_display=["id","domain","parent_site_name","brief","user_id_format_string","tld"]
    #list_filter=["tld"] #TODO doesn't work because options include all shared strings
    readonly_fields=['tld']
    exclude=["user_id_patterns"]
    ordering=['domain']
    inlines=[UrlPatternInline]
    
    def get_search_results(self, request, queryset, search_term):
        queryset.filter(user_id_format_string__isnull=False)
        return super().get_search_results(request, queryset, search_term)

    
# Handled by inlines, reinstate if new fields render it necessary to have these as an admin panel.
# @admin.register(UserName)
# class UserNameAdmin(admin.ModelAdmin):
#     search_fields=["name"]
#     autocomplete_fields=["tags","name","website","belongs_to"]
#     pass

# @admin.register(UserNumber)
# class UserNumberAdmin(admin.ModelAdmin):
#     autocomplete_fields=["belongs_to"]

#     pass