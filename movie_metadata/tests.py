"""Tests for Movie files in HDD-indexer

This module provides testing functions for movie files identified by
hdd-indexer.

Usage:
        $ from movie_metadata import tests
        $ tests.test_name()

Save Movie:
    Tests for saving movie records to database. Currently only saves
    a movie object via movie_metadata.movie.save
        $ save_movie()

Flow:
    Test complete program and data flow. Calls all associated functions
    to get movies on hdd, load metadata, and save to database.

Improve Results:
    Improve metadata for existing movies in database. Checks for missing
    information and tries to download it.

Export:
    Exports list of movies in database to a local text file.
"""

# from django.test import TestCase
from datetime import datetime
from movie_metadata import crawl, load, movie
from movie_metadata.models import Movie


def save_movie():
    """Test saving movie to database

    Saves a sample movie object to database.

    Args:
        None

    Returns:
        0 on Success, None otherwise

    Raises:
        None
    """
    m = {}
    actors = ['A1', 'A2', ]
    directors = ['D1', 'D2', ]
    producers = ['P1', 'P2', ]
    cast = {
        'Actor': actors
    }
    crew = {
        'Director': directors,
        'Producer': producers,
    }

    m['title'] = 'Title'
    m['release'] = datetime.now()
    m['relpath'] = '/'
    m['cast'] = cast
    m['crew'] = crew
    m['imdb_rating'] = 8.9
    m['imdb_url'] = 'imdb.com'
    m['rotten_tomatoes_rating'] = 89
    m['rotten_tomatoes_url'] = 'rottentomatoes.com'

    try:
        movie.save(m)
    except Exception as e:
        print e
        return None
    return 0


def flow():
    """Test program flow

    Calls crawler to get movie files, calls loader to download movie
    metadata info and saves movies to database.

    Args:
        None

    Returns:
        tuple containing -
            saved_list[] - list of movienames saved to database
            skipped_list[] - list of movienmes skipped

    Raises:
        None
    """
    movie_crawler = crawl.get_movies()
    assert movie_crawler is not None
    saved_list = []
    skipped_list = []
    for movie_title, movie_path, imdb_id in movie_crawler:
        print '------------------------------------'
        print movie_title, imdb_id
        print movie_path
        print '------------------------------------'
        m = None
        # movie has been identified by OpenSub
        if imdb_id is not None:
            print 'Searching by IMDb ID'
            m = load.movie_metadata_by_imdb_id(imdb_id)
        # movie has not been identified by OpenSub
        if m is None:
            print 'Searching by filename'
            # IMDb ID not available, or search not available
            m = load.movie_metadata_by_title(movie_title)
        # movie not identified by any means
        if m is None:
            print 'Movie SKIPPED.'
            # No match found by title, or search not available
            skipped_list.append(movie_title)
            continue
        try:
            # save movie only if we get an identified movie
            assert type(m) == dict
            m['relpath'] = movie_path
            movie.save(m)
            saved_list.append(movie_title)
        except AssertionError:
            skipped_list.append(movie_title)

    print '----------------------------------------'
    print '----------------------------------------'
    print ' SKIPPED  ITEMS '
    print '----------------------------------------'
    for item in skipped_list:
        print item

    return (saved_list, skipped_list)


def improve_saved_metadata():
    """Improve metadata for saved movies

    Checks movies saved in database for missing fields and tries
    to download the mising information from the internet.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    movies = Movie.objects.all()
    for m in movies:
        if (
            m.release is None or
            m.actors.all() == [] or
            m.directors.all() == [] or
            m.imdb_score is None
            # TODO: add more missing fields
            # TODO: calculate best JSON source based on missing fields
        ):
            # TODO: case where IMDb ID is None
            r = load.tmdb3_search_by_imdb_id(m.imdb_id)
            if r is None:
                print '----------------------------------'
                print 'File: ', m.relpath
                print 'Title: ', m.title
                print 'The fields detected for this file have some errors.'
                print 'Please correct it through the admin interface.'
                print '----------------------------------'
            else:
                movie.save(r)


def export(
    command='run',
    type='text',
    sort='title',
    path='movies.txt'
):
    """Export list of movies in database to file

    Exports movies stored in database to a text file. The exported
    data can be sorted based on parameters.

    Args:
        command(str):
            help    : display this text
            run     : export to file
        type(str):
            text    : create a text file
        sort(str):
            title   : sort movies by title
            release : sort movies by release date
            imdb_rating: sort movies by IMDb ratings
        path(str): path of file to be exported

    Returns:
        None

    Raises:
        None
    """
    if command == 'help':
        print export.__doc__
        return

    if command != 'run':
        print 'BAD COMMAND.'
        return

    sort_types = {
        'imdb_ratings': lambda: Movie.objects.order_by('imdb_score'),
        'title': lambda: Movie.objects.order_by('title'),
        'release': lambda: Movie.objects.order_by('release'),
    }
    movies = sort_types.get(sort, None)
    if not movies:
        # default to sort by title if args incorrect
        movies = sort_types['title']
    with open(path, 'w') as f:
        for m in movies():
            f.write(m.title)
            f.write(' ')
            f.write(m.relpath)
            f.write('\n')
    print 'Export successful. See ', path,
