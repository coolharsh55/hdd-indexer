"""Models for movie_metadata

    Defines the Movie and related models for use in hdd-indexer.

    Usage:
        $ from movie_metadata.models import ModelName

    Singleton:
        Singletons are used for storing single configuration entries such
        as hdd-name, hdd-root, and movie-folder.
"""

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from django.utils.text import slugify


@python_2_unicode_compatible
class Movie(models.Model):
    """Movie

    Represents a Movie instance in database.

    Attributes:
        title(str): movie title
        release(date): release date
        relpath(str): relative path of the movie file from movie folder
        actors(Actor, ManyToMany): actors in movie
        directors(Director, ManyToMany): directors in movie
        imdb_score(float): IMDb rating
        tomatoes_rating(int): RottenTomatoes rating
        metascore(int): Metacritic rating
        imdb_id(int): IMDb ID of the movie
        slug(str): Slug used for accessing movie in browser
    """
    _id = models.AutoField(primary_key=True)

    # basic information - title, release, poster, relpath
    title = models.CharField(max_length=500,)
    release = models.DateField(blank=True, null=True)
    # TODO: poster = models.ImageField(blank=True,)
    relpath = models.CharField(max_length=500,)

    # cast and crew
    actors = models.ManyToManyField(
        'movie_metadata.Actor',
        blank=True)
    directors = models.ManyToManyField(
        'movie_metadata.Director',
        blank=True)

    # ratings and online links
    imdb_score = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True)
    tomatoes_rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True)
    metascore = models.PositiveSmallIntegerField(
        blank=True,
        null=True)
    imdb_id = models.PositiveIntegerField(
        blank=True,
        null=True)

    # db stuff
    slug = models.SlugField(
        max_length=500,
        editable=False,)

    def __str__(self):
        """String representation of Movie

        Args:
            self: current instance of Movie

        Returns:
            title(str): movie title

        Raises:
            None
        """
        return self.title

    def save(self, *args, **kwargs):
        """Save Movie to database

        create slug based on movie title

        Args:
            self: current instance of Movie
            *args: arguments passed by system
            **kwargs: keyword arguments passed by system

        Returns:
            calls super()

        Raises:
            None
        """
        self.slug = slugify(self.title)
        # TODO: check if relpath is a valid file
        return super(Movie, self).save(*args, **kwargs)


@python_2_unicode_compatible
class Actor(models.Model):
    """Actor in a Movie

    Represents a Person cast as an Actor in a Movie

    Attributes:
        person(Person, OneToOne): Actor as Person
    """
    person = models.OneToOneField('movie_metadata.Person')

    class Meta(object):
        """Meta attributes for Actor

        Attributes:
            ordering: specifies ordering of Actors in admin
        """
        ordering = ['person']

    def __str__(self):
        """String representation of Actor

        Args:
            self: current instance of Actor

        Returns:
            name(str): name of the person

        Raises:
            None
        """
        return self.person.name


@python_2_unicode_compatible
class Director(models.Model):
    """Director in a Movie

    Represents a Person in a Movie crew as Director

    Attributes:
        person(Person, OneToOne): Director as Person
    """
    person = models.OneToOneField('movie_metadata.Person')

    class Meta(object):
        """Meta attributes for Director

        Attributes:
            ordering: specifies ordering of Directors in admin
        """
        ordering = ['person']

    def __str__(self):
        """String representation of Director

        Args:
            self: current instance of Director

        Returns:
            name(str): name of the person

        Raises:
            None
        """
        return self.person.name


@python_2_unicode_compatible
class Person(models.Model):
    """Person associated with a Movie

    Attributes:
        _id(int): primary key for table, autoincrementing
        name(str): name of the person
        slug(str): slug for accessing person in browser
    """
    _id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta(object):
        """Meta attributes for Person

        Attributes:
            ordering: specifies ordering of Person in admin
        """
        ordering = ['name']

    def __str__(self):
        """String representation of Person

        Args:
            self: current instance of Person

        Returns:
            name(str): name of the person

        Raises:
            None
        """
        return self.name

    def save(self, *args, **kwargs):
        """Save Person to database

        calculates slug based on the person's name

        Args:
            self: current instance of Person
            *args: arguments passed by system
            **kwargs: keyword arguments passed by system

        Returns:
            calls super()

        Raises:
            None
        """
        self.slug = slugify(self.name)
        return super(Person, self).save(*args, **kwargs)
