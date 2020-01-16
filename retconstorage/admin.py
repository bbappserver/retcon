from django.contrib import admin
from .models import ManagedFile
# Register your models here.
@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    search_fields=['file']
    # search_fields=['name__name']
    # autocomplete_fields=['name']