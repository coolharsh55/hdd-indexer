"""Interact with Movies stored in database

    The movie module allows interactions with the movie objects stored
    in database. It can save movies, actors, directors, and other models
    associated with Movie.

    Usage:
        $ from movie_metadata import movie
        $ movie.function_name()

    Save Person:
        The save person function uses abstraction to make it possible to
        save all related persons (cast, crew) for a movie with a single
        function.
"""

from movie_metadata.models import Movie
from movie_metadata.models import Person
from movie_metadata.models import Actor
from movie_metadata.models import Director


def save(movie):
    """Save movie object to database

    Save a movie object to database along with its related fields such
    as Person(cast, crew).

    Args:
        movie(dict): dictionary containing movie metadata

    Returns:
        None

    Raises:
        None
    """

    if not movie:
        # print 'Bad request. SKIP.'
        return

    # print 'Saving Movie object... ',
    assert movie.get('title', None) is not None

    # movie exists in database
    if Movie.objects.filter(
            title=movie['title']).exists():
        movie_in_db = Movie.objects.get(
            title=movie['title'])
        # print 'already in database.'
    else:
        # add movie to database
        movie_in_db = Movie()
        # title
        movie_in_db.title = movie['title']
        movie_in_db.save()

    if movie.get('imdb_id', None):
        movie_in_db.imdb_id = movie['imdb_id']
    # release
    if movie.get('release', None):
        movie_in_db.release = movie['release']
    # relative path
    assert movie.get('relpath', None) is not None
    movie_in_db.relpath = movie['relpath']
    # imdb rating
    if movie.get('imdb_rating', None):
        movie_in_db.imdb_score = movie['imdb_rating']
    # rotten tomatoes rating
    if movie.get('tomato_rating', None):
        movie_in_db.tomatoes_rating = movie['tomato_rating']
    # metascore rating
    if movie.get('metascore', None):
        movie_in_db.metascore = movie['metascore']
    # save movie in database
    movie_in_db.save()
    # print 'added metadata to databased.'

    # CAST
    if movie.get('cast', None):
        # print 'Saving cast... '
        _save_person(
            movie_in_db.title,
            movie_in_db.actors,
            movie['cast']['Actor'],
            role=Actor)

    # CREW - DIRECTORS
    if movie.get('crew', None):
        # print 'Saving crew(directors)... '
        _save_person(
            movie_in_db.title,
            movie_in_db.directors,
            movie['crew']['Director'],
            role=Director)


def _save_person(movie_title, movie_role, person_list, role):
    """Save person associated with movie to database

    Save person can save persons associated with movies in various
    roles to the database. It uses abstraction to define Role, which
    can be anything from cast or crew.

    Args:
        movie_title(str): title of the movie existing in database
        movie_role(set): Movie model set for associate Persons
        person_list(list): list of Persons to be added
        role(Person): class inherited from Person associated with Movie
            such as Actor, Director, etc.

    Returns:
        None

    Raises:
        None
    """
    for person in person_list:
        # print person,
        # check if person is in database
        if not Person.objects.filter(name=person).exists():
            # if not, save person to database
            p = Person(name=person)
            p.save()
            # print ' added to database.',
        else:
            # print ' exists in database.',
            pass

        person = Person.objects.get(name=person)
        # check if person exists in given role
        if not role.objects.filter(person=person).exists():
            # if not, add person in role to database
            p = role(person=person)
            p.save()
            # print 'Added in role.',

        person = role.objects.get(person=person)
        # check if person is associated with movie in given role
        if not person.movie_set.filter(title=movie_title).exists():
            # if not, add person to movie in role
            movie_role.add(person)
            # print 'Added to movie.',
