import datetime
from typing import Any, Optional, Sequence, Type, Union
import django
from django.contrib import admin
from django.forms.widgets import Widget
from .models import Genre,Series,WebVideo,Movie,Episode,Company,RelatedSeries,Illustration,Title,CreativeWork,Portrayal,Character
from semantictags.admin import TaggableAdminMixin
from django.forms import ModelForm,FileField, ValidationError

class ExternalContentInline(admin.TabularInline):
    model=CreativeWork.external_representations.through
    extra=1
    verbose_name="External URL"
    verbose_name_plural="External URLs"
    autocomplete_fields=["contentresource"]

class CompanyExternalContentInline(admin.TabularInline):
    model=Company.external_representations.through
    extra=1
    verbose_name="External URL"
    verbose_name_plural="External URLs"
    autocomplete_fields=["contentresource"]

class FilesInline(admin.TabularInline):
    model=CreativeWork.files.through
    extra=1
    verbose_name="Files"
    verbose_name_plural="Files"
    autocomplete_fields=["managedfile"]


class RelatedSeriesInline(admin.TabularInline):
    model=RelatedSeries
    fk_name = "to_series"
    autocomplete_fields=('from_series',)

class LocalizedTitleInline(admin.TabularInline):
    model=Title
    fk_name = "creative_work"
    autocomplete_fields=('language',)

class PortrayalInline(admin.TabularInline):
    model=Portrayal
    fk_name = "episode"
    autocomplete_fields=('actor','role')

@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    search_fields=['name__name']
    autocomplete_fields=['name']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields=['name__name']
    autocomplete_fields=['name']

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields=['name']
    autocomplete_fields=['tags','ambiguous_tags','produced_by','published_by','created_by','parent_series']
    readonly_fields = ('episodes_human_readable',)
    exclude=["external_representations","files"]
    inlines=(RelatedSeriesInline,LocalizedTitleInline,ExternalContentInline,FilesInline)


#Not properly binding media type so disabled
# @admin.register(Movie)
# class MovieAdmin(TaggableAdminMixin):
#     autocomplete_fields=['tags','ambiguous_tags','part_of','created_by','published_by']
#     exclude=["external_representations",'medium','files']
#     inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline)

from django.forms import DateField
class FuzzyDateField(DateField):
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
                 
    def clean(self, value: Any) -> Any:
        return value

from dateparser.date import DateDataParser
class CreativeWorkAdminFormBase(ModelForm):
    file=FileField(required=False,label="Add Uploaded File Hash")
    published_on =FuzzyDateField(required=False)
    #TODO now that I understand custom fields we can probably use string with x to indicate don't care
    def clean(self):
        ddp = DateDataParser(settings={'DATE_ORDER': 'YMD'})
        d=ddp.get_date_data(self.cleaned_data['published_on'])
        self.cleaned_data['published_on']=d['date_obj']
        
        if self.cleaned_data['published_on'] is not None:
            m_precis={'day':CreativeWork.DATE_PRECISION_DAY,'month':CreativeWork.DATE_PRECISION_MONTH,'year':CreativeWork.DATE_PRECISION_YEAR}
            self.cleaned_data['published_on_precision']=m_precis[d['period']]
        
        cleaned_data = super().clean()

        #DateData(date_obj=datetime.datetime(2014, 1, 24, 12, 49), period='day', locale='nl')
        if 'published_on' in cleaned_data and 'published_on_precision' not in cleaned_data:
            raise ValidationError("if a publication date is supplied you must also supply precison")
        
@admin.register(Episode)
class EpisodeAdmin(TaggableAdminMixin):
    autocomplete_fields=['tags','ambiguous_tags','part_of','published_by','created_by']
    exclude=["external_representations","files"]
    list_display=['preferred_name','name','published_on','publisher_names','part_of']
    list_editable=['part_of']
    search_fields=['name','localized_titles__name','published_by__name']
    inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline,PortrayalInline)
    actions=['set_date_precision_to_year','set_date_precision_to_month','set_date_precision_to_day']
    
    def set_date_precision_to_year(modeladmin, request, queryset):
        queryset.all().update(published_on_precision=Episode.DATE_PRECISION_YEAR)
    def set_date_precision_to_month(modeladmin, request, queryset):
        queryset.all().update(published_on_precision=Episode.DATE_PRECISION_MONTH)
    def set_date_precision_to_day(modeladmin, request, queryset):
        queryset.all().update(published_on_precision=Episode.DATE_PRECISION_DAY)
        
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.prefetch_related('part_of').prefetch_related('published_by')
        return queryset
    
        
    
    def get_form(self, request, obj=None, **kwargs):
        if request.user.is_superuser:
            kwargs['form'] = CreativeWorkAdminFormBase
        return super().get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj : Episode, form, change):
        super().save_model(request, obj, form, change)
        
        if 'file' in request.FILES:
            obj.attach_file_with_blob(request.FILES['file'].chunks())
    
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields=['name','tags','parent','ambiguous_tags',]
    search_fields=['name',]
    list_display=['name','defunct','parent',]
    list_editable=['defunct','parent',]
    list_filter=['defunct']
    inlines=(CompanyExternalContentInline,)
    #allowing sort by name actually sorts on shadredsting_id which is wrong, but the model's default ordering is correct
    sortable_by=['defunct','parent',] 
    exclude=["external_representations"]
    pass

@admin.register(Illustration)
class IllustrationAdmin(admin.ModelAdmin):
        autocomplete_fields=['tags','ambiguous_tags','published_by','illustrators','created_by']
        exclude=["external_representations","files"]
        inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline)

