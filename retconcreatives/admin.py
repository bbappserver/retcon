from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie,Episode,Company,RelatedSeries
from semantictags.admin import TaggableAdminMixin

class RelatedCreativeWorkInline(admin.TabularInline):
    model=RelatedSeries
    fk_name = "to_series"

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields=['name__name']
    autocomplete_fields=['name']

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields=['name','tags']
    autocomplete_fields=['tags','ambiguous_tags','produced_by','published_by']
    #readonly_fields = ('related_from_series',)
    inlines=(RelatedCreativeWorkInline,)


@admin.register(Movie)
class MovieAdmin(TaggableAdminMixin):
    autocomplete_fields=['tags','ambiguous_tags','part_of']

@admin.register(Episode)
class EpisodeAdmin(TaggableAdminMixin):
    autocomplete_fields=['tags','ambiguous_tags','part_of']

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    autocomplete_fields=['name','tags','parent','ambiguous_tags','website']
    search_fields=['name','website__name']
    pass