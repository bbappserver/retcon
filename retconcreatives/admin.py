from django.contrib import admin
from .models import Genre,Series,WebVideo,Movie

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    pass

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    pass
