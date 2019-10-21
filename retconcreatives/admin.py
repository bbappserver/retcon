from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie,Episode
from semantictags.admin import TaggableAdmin
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields=['name__name']
    autocomplete_fields=['name']

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields=['name','tags']
    autocomplete_fields=['tags']

@admin.register(Movie)
class MovieAdmin(TaggableAdmin):
    autocomplete_fields=['tags','part_of']

@admin.register(Episode)
class EpisodeAdmin(TaggableAdmin):
    autocomplete_fields=['tags','part_of']