"""Admin for movie_metadata

    MovieAdmin

"""

from django.contrib import admin

from movie_metadata.models import Movie
from movie_metadata.models import Actor
from movie_metadata.models import Director
from movie_metadata.models import Person


class MovieActorInline(admin.TabularInline):
    """Show movies inline on Actor forms
    """
    model = Movie.actors.through


class MovieDirectorInline(admin.TabularInline):
    """Show movies inline on Director forms
    """
    model = Movie.directors.through


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """Admin for Movie class
    """
    # display fields in movie index
    list_display = (
        'title',
        'release',
        'relpath',
        'imdb_score',
        'tomatoes_rating',
        'metascore'
    )
    # sort columns
    ordering = (
        'title',
        'release',
        'imdb_score',
        'tomatoes_rating',
        'metascore'
    )
    # search based on fields
    search_fields = (
        'title',
        'relpath',
    )
    # sort based on date field
    date_hierarchy = 'release'
    # filter results based on fields
    list_filter = (
        'actors',
        'directors',
    )
    # horizontal multi-select columns in movie edit forms
    filter_horizontal = (
        'actors',
        'directors',
    )
    # read-only fields in forms
    readonly_fields = ('_id',)
    # inlines = [ActorInline, ]


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    """Admin for Actors
    """
    list_display = (
        'name',
        'no_movies',
        'is_director',
        'directed',
    )

    def name(self, obj):
        """Actor Name
        """
        return obj.person.name

    def no_movies(self, obj):
        """No of movies acted in
        """
        return obj.movie_set.count()
    no_movies.short_description = 'Movies acted in'

    def is_director(self, obj):
        """Is also a director?
        """
        try:
            if obj.person.director:
                return True
        except Exception:
            pass
        return False
    is_director.short_description = 'Director?'
    is_director.boolean = True

    def directed(self, obj):
        """No of Movies directed
        """
        try:
            if obj.person.director is not None:
                return obj.person.director.movie_set.count()
        except Exception:
            pass
        return 0
    directed.short_description = 'Movies Directed'

    search_fields = ('person__name',)
    readonly_fields = ('person',)

    fieldsets = (
        ('Person', {
            'fields': (
                'person',
            )
        }),
    )
    inlines = [MovieActorInline, ]


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    """Admin for Directors
    """
    list_display = (
        'name',
        'no_movies',
        'is_actor',
        'acted',
    )

    def name(self, obj):
        """Director Name
        """
        return obj.person.name

    def no_movies(self, obj):
        """No of movies directed
        """
        return obj.movie_set.count()
    no_movies.short_description = 'Movies directed'

    def is_actor(self, obj):
        """Is also an actor?
        """
        try:
            if obj.person.actor:
                return True
        except Exception:
            pass
        return False
    is_actor.short_description = 'Actor?'
    is_actor.boolean = True

    def acted(self, obj):
        """No of Movies acted in
        """
        try:
            if obj.person.actor is not None:
                return obj.person.actor.movie_set.count()
        except Exception:
            pass
        return 0
    acted.short_description = 'Movies acted in'

    search_fields = ('person__name',)
    readonly_fields = ('person',)

    fieldsets = (
        ('Person', {
            'fields': (
                'person',
            )
        }),
    )

    inlines = [MovieDirectorInline, ]


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """Admin for Actors
    """
    list_display = (
        'name',
        'no_movies',
        'is_actor',
        'acted',
        'is_director',
        'directed',
    )

    def no_movies(self, obj):
        """No of movies acted in
        """
        # return obj.movie_set.count()
        return 0

    def is_actor(self, obj):
        """Is also an actor?
        """
        try:
            if obj.actor:
                return True
        except Exception:
            pass
        return False
    is_actor.short_description = 'Actor?'
    is_actor.boolean = True

    def acted(self, obj):
        """No of Movies acted in
        """
        try:
            if obj.actor is not None:
                return obj.actor.movie_set.count()
        except Exception:
            pass
        return 0
    acted.short_description = 'Movies acted in'

    def is_director(self, obj):
        """Is also a director?
        """
        try:
            if obj.director:
                return True
        except Exception:
            pass
        return False
    is_director.short_description = 'Director?'
    is_director.boolean = True

    def directed(self, obj):
        """No of Movies directed
        """
        try:
            if obj.director is not None:
                return obj.director.movie_set.count()
        except Exception:
            pass
        return 0
    directed.short_description = 'Movies Directed'

    search_fields = ('name',)

    fieldsets = (
        ('Person', {
            'fields': (
                'name',
            )
        }),
    )
