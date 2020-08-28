from django.contrib import admin
from .models import ContentResource,EphemeralResource
# Register your models here.

@admin.register(ContentResource,EphemeralResource)
class ExternalContentAdmin(admin.ModelAdmin):
    search_fields=["url"]
    readonly_fields = ["date_added"]
    
    def date_added(self,instance):
        return str(instance.date_added)

# class ExternalContentInline(admin.TabularInline):
#     model=ContentResource