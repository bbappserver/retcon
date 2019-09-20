from django.contrib import admin

# Register your models here.

from .models import TagLabel,Tag,Taggable

@admin.register(TagLabel)
class TagLabelAdmin(admin.ModelAdmin):
    search_fields = ['label']
    read_only_fields=['tag']
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    autocomplete_fields = ['labels']
    search_fields = ['labels__label__name']
    pass

class TaggableAdmin(admin.ModelAdmin):
    autocomplete_fields=['tags__labels']