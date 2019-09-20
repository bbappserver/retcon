from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie
from semantictags.admin import TaggableAdmin
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields=['name__name']

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    search_fields=['name']

@admin.register(Movie)
class MovieAdmin(TaggableAdmin):
    autocomplete_fields=['tags','name','part_of']
