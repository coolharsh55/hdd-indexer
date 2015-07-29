"""Admin for movie_metadata

    MovieAdmin

"""

from django.contrib import admin

from movie_metadata.models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin for Movie class
    """
    # display fields in movie index
    list_display = (
        'title', 'release', 'relpath',
        'imdb_score', 'tomatoes_rating', 'metascore'
    )
    # sort columns
    ordering = (
        'title', 'release',
        'imdb_score', 'tomatoes_rating', 'metascore'
    )
    # search based on fields
    search_fields = ('title', 'relpath', )
    # sort based on date field
    date_hierarchy = 'release'
    # filter results based on fields
    list_filter = ('actors', 'directors', )
    # horizontal multi-select columns in movie edit forms
    filter_horizontal = ('actors', 'directors', )
    # read-only fields in forms
    readonly_fields = ('_id',)
