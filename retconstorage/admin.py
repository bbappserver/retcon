from django.contrib import admin
from .models import ManagedFile,NamedFile,Filetype
# Register your models here.

@admin.register(Filetype)
class FiletypeAdmin(admin.ModelAdmin):
    pass

@admin.register(NamedFile)
class NamedFileAdmin(admin.ModelAdmin):
    exclude=('identity',)
    list_filter = ('identity__filetype__MIME',)
    def get_readonly_fields(self, request, obj=None):
        # all fields are readonly in admin
        return [f.name for f in self.model._meta.fields]

@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    search_fields=['sha256']
    list_filter = ('filetype__MIME',)
    # search_fields=['name__name']
    # autocomplete_fields=['name']


