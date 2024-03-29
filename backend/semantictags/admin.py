from typing import Sequence
from django.contrib import admin
from django.conf import settings
from django.http.request import HttpRequest
# Register your models here.

from .models import TagLabel,Tag,Taggable,TaggableWithExtras
from sharedstrings.models import Language


class TagDefinitionInline(admin.StackedInline):
    model = Tag.labels.through
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
    autocomplete_fields=["canonical_label","distinguish_from","implies","conflicts_with"]
    search_fields = ['labels__label__name']

    list_display=['id','canonical_label','definition']

    def get_search_results(self, request, queryset, search_term):
        queryset=Tag.objects.filter(labels__label__icontains=search_term )
        queryset = queryset | Tag.objects.filter(canonical_label__label__istartswith=search_term )
        return queryset,True

class TaggableAdminMixin(admin.ModelAdmin):
    autocomplete_fields=['tags__labels','ambiguous_tags']
    
    def get_list_filter(self, request: HttpRequest) -> Sequence[str]:
        l= list(super().get_list_filter(request))
        t=self.get_queryset(request).model
        if hasattr(t,'is_favourite') and 'is_favourite' not in l:
            l.append('is_favourite')
        return l
    
    def get_fieldsets(self,request, obj=None):
        #fieldsets= super().get_fieldsets(request,obj)
        
        if issubclass(self.model,TaggableWithExtras):
            f = list(self.get_fields(request,obj))
            
            #TODO get user's preference
            collapse=True
            for fr in ["is_favourite", "notes"]:
                f.remove(fr)
            fieldsets = [
            (
                None,
                {
                    "fields": f,
                },
            ),
            (
                "Extras",
                {
                    "classes": ["collapse"] if collapse else [],
                    "fields": ["is_favourite", "notes"],
                },
            )]
            return fieldsets
        else:
            return super().get_fieldsets(request,obj=obj)