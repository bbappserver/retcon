from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie,Episode,Company,RelatedSeries,Illustration,Title,CreativeWork,Portrayal,Character
from semantictags.admin import TaggableAdminMixin

class ExternalContentInline(admin.TabularInline):
    model=CreativeWork.external_representation.through
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
    exclude=["external_representation","files"]
    inlines=(RelatedSeriesInline,LocalizedTitleInline,ExternalContentInline,FilesInline)


#Not properly binding media type so disabled
# @admin.register(Movie)
# class MovieAdmin(TaggableAdminMixin):
#     autocomplete_fields=['tags','ambiguous_tags','part_of','created_by','published_by']
#     exclude=["external_representation",'medium','files']
#     inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline)

@admin.register(Episode)
class EpisodeAdmin(TaggableAdminMixin):
    autocomplete_fields=['tags','ambiguous_tags','part_of','published_by','created_by']
    exclude=["external_representation","files"]
    inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline,PortrayalInline)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields=['name','tags','parent','ambiguous_tags','website']
    search_fields=['name','website__name']
    exclude=["external_representation"]
    pass

@admin.register(Illustration)
class IllustrationAdmin(admin.ModelAdmin):
        autocomplete_fields=['tags','ambiguous_tags','published_by','illustrators','created_by']
        exclude=["external_representation","files"]
        inlines=(LocalizedTitleInline,ExternalContentInline,FilesInline)

