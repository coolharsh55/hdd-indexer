"""comparator module

compare movie metadata across disks to generate lend/borrow lists
the comparing file has to be a valid json file or stream
and must contain data in the format:
    movie: {
        id: {
            imdb_id
            title
            release
        }
    }
"""

import logging
import json
import traceback
log = logging.getLogger('comparator')
log.info(72 * '-')
log.info('comparator loaded')

from movie_metadata.models import Movie


def load_data(datastream):
    """load data from file

    load json data from file and construct models from it
    """
    pass


def calculate_take(this, that):
    """calculate list of things to take
    """
    pass


def calculate_give(this, that):
    """calculate list of things to give
    """
    pass


def compare(datastream):
    """compare the data in the datastream with that present in the database
    datastream must be a valid json file

    Args:
        datastream(stream): valid json stream

    Returns:
        stream: give list of tuples (imdb_id, title)
        stream: take list of tuples (imdb_id, title)
    """
    try:
        assert datastream is not None
    except AssertionError:
        log.error(traceback.format_exec())
        return None

    with open('/tmp/tmpfile.txt', 'w') as fd:
        for chunk in datastream.chunks():
            fd.write(chunk)
    with open('/tmp/tmpfile.txt', 'r') as datastream:
        data = json.load(datastream)

    that = {}
    items = data.values()[:3]
    for movie in items:
        that[movie['imdb_id']] = (
            movie['imdb_id'], movie['title'], movie['release_date'])
    # print that.keys()

    this = {}
    movies = Movie.objects.all()[:3]
    movies = movies
    for movie in movies:
        this[movie.imdb_id] = (movie.imdb_id, movie.title, movie.release)
    # print this.keys()

    that_set = set(that.keys())
    this_set = set(this.keys())

    # take: movies in that but not in this = that - this
    take_set = that_set.difference(this_set)
    # print 'take:', take_set
    take_list = []
    for key in take_set:
        take_list.append(that[key])
    print take_list

    # give: movies in this but not in that = this - that
    give_set = this_set.difference(that_set)
    # print 'give:', give_set
    give_list = []
    for key in give_set:
        give_list.append(this[key])
    print give_list

    return take_list, give_list
