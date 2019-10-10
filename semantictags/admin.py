from django.contrib import admin
from django.conf import settings
# Register your models here.

from .models import TagLabel,Tag,Taggable
from sharedstrings.models import Language


class TagDefinitionInline(admin.StackedInline):
    model = TagLabel.definitions.through
    extra = 1
    autocomplete_fields=["tag"]

class TagLabelInline(admin.StackedInline):
    model = Tag.labels.through
    extra = 3
    autocomplete_fields=["taglabel"]

# @admin.register(TagLabel.definitions.through)
# class TagLabelAdmin(admin.ModelAdmin):
#     autocomplete_fields = ['tag']


@admin.register(TagLabel)
class TagLabelAdmin(admin.ModelAdmin):
    search_fields = ['label']
    autocomplete_fields=["language"]
    list_display = ['label','language']
    list_filter = [['language',admin.RelatedOnlyFieldListFilter]]
    inlines=[TagDefinitionInline]
    def get_changeform_initial_data(self, request):
        lang=None
        try:
            lang = request.LANGUAGE_CODE
        except:
            lang = settings.LANGUAGE_CODE
        
        try:
            lang=Language.objects.get(isocode=lang)
        except:
            return {}
            
        return {'language': lang}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = [TagLabelInline]
    exclude=["labels"]
    autocomplete_fields=["canonical_label","distinguish_from","implies"]
    search_fields = ['labels__label__name']

    list_display=['id','canonical_label','definition']

    def get_search_results(self, request, queryset, search_term):
        queryset=Tag.objects.filter(labels__label__icontains=search_term )
        queryset = queryset | Tag.objects.filter(canonical_label__label__istartswith=search_term )
        return queryset,True

class TaggableAdmin(admin.ModelAdmin):
    autocomplete_fields=['tags__labels']
    