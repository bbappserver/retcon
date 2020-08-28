from django.contrib import admin
from django.db.transaction import atomic
from .models import ManagedFile,NamedFile,Filetype
# Register your models here.

@admin.register(Filetype)
class FiletypeAdmin(admin.ModelAdmin):
    pass

@admin.register(NamedFile)
class NamedFileAdmin(admin.ModelAdmin):
    search_fields=['name']
    list_filter = ('identity__filetype__MIME',)
    list_display = ('name','display_size','display_MIME','multiplicity','deduped_multiplicity')
    actions=['delete_and_unlink_selected_names','purge_files','increment_retain_count','decrement_retain_count']


    def get_readonly_fields(self, request, obj=None):
        # all fields are readonly in admin
        l=[f.name for f in self.model._meta.fields]
        l.append('alternate_names')
        return l
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset=queryset.filter(name__icontains=search_term)
        return queryset, use_distinct
    
    def delete_and_unlink_selected_names(modeladmin, request, queryset):
        for f in queryset:
            f.unlink()
            f.delete()
    @atomic
    def increment_retain_count(modeladmin, request, queryset):
        for f in queryset:
            f.identity.retain()
    @atomic
    def decrement_retain_count(modeladmin, request, queryset):
        for f in queryset:
            f.identity.retain()
    
    def purge_files(modeladmin, request, queryset):
        for f in queryset:
            if f.identity:
                f.identity.purge()
        #purge_files.short_description = "Remove all named files and tracked files, marking as record as deleted"
    def get_actions(self, request):
        #Disable delete
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    search_fields=['sha256']
    list_filter = ('filetype__MIME',)
    def get_readonly_fields(self, request, obj=None):
        return ['strnames']
    def get_search_results(self, request, queryset, search_term):
        #queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        search_term=bytes.fromhex(search_term)
        queryset=ManagedFile.objects.filter(sha256=search_term)
        return queryset,True


