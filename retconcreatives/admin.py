from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie,Episode,Company,RelatedSeries,Illustration,Title,CreativeWork
from semantictags.admin import TaggableAdminMixin

class ExternalContentInline(admin.TabularInline):
    model=CreativeWork.external_representation.through
    extra=1
    verbose_name="External URL"
    verbose_name_plural="External URLs"


class RelatedSeriesInline(admin.TabularInline):
    model=RelatedSeries
    fk_name = "to_series"
    autocomplete_fields=('from_series',)

class LocalizedTitleInline(admin.TabularInline):
    model=Title
    fk_name = "creative_work"
    autocomplete_fields=('language',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields=['name__name']
    autocomplete_fields=['name']

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields=['name']
    autocomplete_fields=['tags','ambiguous_tags','produced_by','published_by','created_by','parent_series']
    #readonly_fields = ('related_from_series',)
    exclude=["external_representation"]
    inlines=(RelatedSeriesInline,LocalizedTitleInline,ExternalContentInline)


@admin.register(Movie)
class MovieAdmin(TaggableAdminMixin):
    autocomplete_fields=['tags','ambiguous_tags','part_of']

@admin.register(Episode)
class EpisodeAdmin(TaggableAdminMixin):
    autocomplete_fields=['tags','ambiguous_tags','part_of','published_by','created_by']
    exclude=["external_representation"]
    inlines=(LocalizedTitleInline,ExternalContentInline)

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields=['name','tags','parent','ambiguous_tags','website']
    search_fields=['name','website__name']
    pass

@admin.register(Illustration)
class IllustrationAdmin(admin.ModelAdmin):
        autocomplete_fields=['tags','ambiguous_tags','published_by','illustrators','created_by']
        exclude=["external_representation"]
        inlines=(LocalizedTitleInline,ExternalContentInline)

