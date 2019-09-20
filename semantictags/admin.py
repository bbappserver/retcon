from django.contrib import admin

# Register your models here.

from .models import TagLabel,Tag,Taggable


class TagDefinitionInline(admin.StackedInline):
    model = TagLabel.definitions.through
    extra = 3

@admin.register(TagLabel.definitions.through)
class TagLabelAdmin(admin.ModelAdmin):
    autocomplete_fields = ['tag']


@admin.register(TagLabel)
class TagLabelAdmin(admin.ModelAdmin):
    search_fields = ['label']
    read_only_fields=['tags']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    autocomplete_fields = ['labels']
    search_fields = ['labels__label__name']
    def get_search_results(self, request, queryset, search_term):
        queryset=Tag.objects.filter(labels__label__icontains=search_term)
        return queryset,False

class TaggableAdmin(admin.ModelAdmin):
    autocomplete_fields=['tags__labels']
    