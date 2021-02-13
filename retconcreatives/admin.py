from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie,Episode,Company,RelatedSeries,Illustration,Title,CreativeWork,Portrayal,Character
from semantictags.admin import TaggableAdminMixin

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
    #readonly_fields = ('related_from_series',)
    exclude=["external_representations","files"]
    inlines=(RelatedSeriesInline,LocalizedTitleInline,ExternalContentInline,FilesInline)


#Not properly binding media type so disabled
# @admin.register(Movie)
# class MovieAdmin(TaggableAdminMixin):
#     autocomplete_fields=['tags','ambiguous_tags','part_of','created_by','published_by']
#     exclude=["external_representations",'medium','files']
#     inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline)

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

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields=['name','tags','parent','ambiguous_tags','website']
    search_fields=['name','website__name']
    list_display=['name','defunct','parent','website']
    list_editable=['defunct','parent','website']
    list_filter=['defunct']
    inlines=(CompanyExternalContentInline,)
    #allowing sort by name actually sorts on shadredsting_id which is wrong, but the model's default ordering is correct
    sortable_by=['defunct','parent','website'] 
    exclude=["external_representations"]
    pass

@admin.register(Illustration)
class IllustrationAdmin(admin.ModelAdmin):
        autocomplete_fields=['tags','ambiguous_tags','published_by','illustrators','created_by']
        exclude=["external_representations","files"]
        inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline)

