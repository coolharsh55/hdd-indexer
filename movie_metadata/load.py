"""Download movie metadata from online sources

    The load module uses OpenSubtitles to try and identify movie
    and get it's IMDb ID. If this cannot be retrieved, it uses
    the filename to perform a movie-title search using external API.
    If the IMDb ID cannot be retrieved, the movie is considered as
    skipped by the load module. Using the retrived IMDb ID, load
    downloads movie metadata from online sources. It currently
    uses two services -
        - OMDb and TMDb for retrieving the metadata.
        - TMDb is tried first, failing which OMDb is accessed

    Usage:
        $ from movie_metadata import load
        $ load.function_name()

    OpenSub key:
        This module uses the OpenSubtitles library, which requires an
        API key for identifying the movie. This key is stored in
        OpenSub_key

    TMDb key:
        This module uses the TMDb APIv3 via the tmdb3 library, which
        requires a key for their API use. The key is set via the
        tmdb_set_key method in the module code.

"""

# TODO: check which service is online and use that
# TODO: check which fields are empty and fill those
# TODO: change name `loader` to `loading`
# TODO: IMDb API for metadata
# TODO: RT API for metadata
# TODO: Metacritic API for metadata
# TODO: see IMDBPie https://github.com/richardasaurus/imdb-pie
# TODO: see imdbpy http://imdbpy.sourceforge.net
# TODO: use only if API keys are not empty
# TODO: use opensub_initiate to get token within threads

from __future__ import unicode_literals
from datetime import datetime
from tmdb3 import searchMovie
from tmdb3 import Movie as tmdbMovie
from tmdb3 import set_key as tmdb_set_key
from os import path
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
from xmlrpclib import ProtocolError
from hdd_settings.models import HDDRoot
from hdd_settings.models import MovieFolder
from movie_metadata.models import Movie
from hdd_settings.models import TMDbKey
from hdd_settings.models import OpenSubKey
from movie_metadata.movie import save as movie_save
import json
import Queue
from threading import Thread
import urllib2
import re


_ERROR = {
    1: 'HDD Root not configured properly.',
    2: 'Movie Folder not configured properly.',
}
"""Crawler Error messages
"""


def loader_status(key=None, value=None):
    """Loader status

    Args:
        key(dict key): key to search in dict
        value(dict value): value to assign to key

    Returns:
        status(bool): True for ON, False for OFF

    """
    if 'status' not in loader_status.__dict__:
        loader_status.status = {
            'STATUS': False,
            'MOVIES_EVALUATED': 0,
            'METADATA_DOWNLOADED': 0,
            'MOVIES_SKIPPED': 0,
            'SKIPPED_LIST': [],
        }
    _LOADER = loader_status.status
    if _LOADER.get(key) is not None:
        if value is not None:
            _LOADER[key] = value
        else:
            return _LOADER[key]
    return _LOADER['STATUS']


def opensub_initiate():
    """OpenSubtitlies initiation for use

    Login to OpenSubtitlies using API to retrieve a token
    for identifying movies.

    Failure results in a null token.
    Network errors are caused to service unavailability, or DNS problems

    Args:
        None

    Returns:
        token(str): Authentication Token for OpenSubtitles
        None: if token cannot be validated

    Raises:
        None
    """
    sub = OpenSubtitles()
    try:
        # login to opensub using API
        token = sub.login(OpenSubKey.get_solo().uid, OpenSubKey.get_solo().key)
        if token:
            return sub
    except AssertionError as e:
        print 'Failed to authenticate opensubtitles login.'
        print e
    except ProtocolError as e:
        """
        TODO: gaierror:
            [Errno 8] nodename nor servname provided, or not known
        """
        if e.errcode == 503:
            # ProtocolError - 503 Service Unavailable
            print 'Check network connection and try again.'
            print e.errmsg
    except Exception as e:
        # Other errors
        print 'Network error.'
        print e


def _run():
    """Run the loader

    Downloads metadata from online sources for movies in database.
    Uses Queue for concurrent access using parallel threads.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    tmdb_set_key(TMDbKey.get_solo().key)
    # TODO: wrap the entire func in try block
    t_size = 5  # size of thread, and movie queue
    # download job queue
    q = Queue.LifoQueue()
    # movies to be saved to database
    m = Queue.Queue()
    # skipped movies
    s = []
    movies = list(Movie.objects.all())
    print 'movies in db: ', len(movies)
    m_start = 0
    loader_status('MOVIES_EVALUATED', 0)
    loader_status('METADATA_DOWNLOADED', 0)
    loader_status('MOVIES_SKIPPED', 0)

    m_list = movies[m_start:m_start + t_size]
    while m_list:
        if loader_status('STATUS') is False:
            break
        for movie in m_list:
            # initialize the job queue
            q.put(movie)

        for i in range(5):
            # start threads
            thread = Thread(target=_load, args=(q, m, s))
            thread.daemon = True
            thread.start()

        # wait for threads to finish
        q.join()

        while not m.empty():
            # save movies to database
            # When movies are saved from within threads, SQLite throws
            # concurrency errors since it cannot handle so many locks
            # An alternate solution is to download the data usnig threads,
            # and then to save movies in a single thread.
            movie, data = m.get()
            movie.delete()
            try:
                movie_save(data)
            except Exception:
                s.append(movie.title)
                movie.save()

            m.task_done()
        m_start += t_size
        m_list = movies[m_start:m_start + t_size]

    loader_status('SKIPPED_LIST', s)
    loader_status('STATUS', False)


def _load(q, m, s):
    """Load metadata from online sources

    Gets a movie from the job q,
    Downloads JSON from online, parses it,
    and saves it to the movie save queue m.

    Args:
        q(Queue): movie object queue to be processed
        m(Queue): movie object queue to be saved
        s(List): movies skipped

    Returns:
        None

    Raises:
        None
    """
    while not q.empty():
        if not loader_status('STATUS'):
            # loader has been turned off
            while not q.empty():
                q.get()
                q.task_done()
            return
        # get a movie object from q
        movie = q.get()

        data = None
        if movie.imdb_id is not None:
            # get metadata by imdb id
            data = movie_metadata_by_imdb_id(movie.imdb_id)
        if data is None:
            # get metadata by title (or filename)
            # can also mean imdb id is not available
            data = movie_metadata_by_title(movie.title)
        if data is not None:
            # movie has metadata
            data['relpath'] = movie.relpath
            m.put((movie, data))
            loader_status(
                'MOVIES_EVALUATED',
                loader_status('MOVIES_EVALUATED') + 1
            )
            loader_status(
                'METADATA_DOWNLOADED',
                loader_status('METADATA_DOWNLOADED') + 1
            )
        else:
            # movie metadata could not be downloaded
            # use opensub to try and identify the movie
            imdb_id = opensub(movie.relpath)
            if imdb_id is None:
                # opensub could not identify the movie
                # print movie.title, ' SKIPPED.'
                loader_status(
                    'MOVIES_EVALUATED',
                    loader_status('MOVIES_EVALUATED') + 1
                )
                loader_status(
                    'MOVIES_SKIPPED',
                    loader_status('MOVIES_SKIPPED') + 1
                )
                s.append(movie.title)

            else:
                # opensub identified movie
                movie.imdb_id = imdb_id
                # put it back in the queue to download its metadata
                # the next time a thread retrieves it
                q.put(movie)
        q.task_done()


def opensub(relpath):
    """OpenSubtitle identification of movie

    Uses the OpenSubtitles API to identify movie

    Args:
        relpath(str): relative path of movie file

    Returns:
        imdb_id(int): on success, returns idetified imdb id
        None: on failure

    Raises:
        None
    """
    sub = OpenSubtitles()
    try:
        # login to opensub using API
        token = sub.login(OpenSubKey.get_solo().uid, OpenSubKey.get_solo().key)
        if not token:
            # return sub
            print 'null token'
            return
        # check that the file is accessible
        if not path.exists(path.join(
            HDDRoot.get_solo().path,
            MovieFolder.get_solo().relpath,
            relpath,
        )):
            print "ERROR: " + relpath
            return
        f = File(path.join(
            HDDRoot.get_solo().path,
            MovieFolder.get_solo().relpath,
            relpath,
        ))
        if f is None:
            return
        hash = f.get_hash()
        size = f.size
        data = sub.search_subtitles([{
            'sublanguageid': 'all',
            'moviehash': hash,
            'moviebytesize': size,
        }])
        if type(data) is list:
            if data[0].get('IDMovieImdb', None):
                return data[0]['IDMovieImdb']
    except ProtocolError as e:
        # most likely network error or API server error
        print "E: " + str(e)
    except AssertionError as e:
        print 'Failed to authenticate opensubtitles login.'
        print e
    except ProtocolError as e:
        """
        TODO: gaierror:
            [Errno 8] nodename nor servname provided, or not known
        """
        if e.errcode == 503:
            # ProtocolError - 503 Service Unavailable
            print 'Check network connection and try again.'
            print e.errmsg
    except Exception as e:
        # Other errors
        print 'Network error.'
        print e


def movie_metadata_by_title(movie_title):
    """Retrieve movie metadata by title

    Searches for movies based on their title and retrieves their
    metadata from online sources. Uses TMDb as first choice,
    failing which OMDb is queried.

    Args:
        movie_title(str): title of the movie to be searched

    Returns:
        movie(dict): a dictionary containing the movie metadata
        or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
                metascore(int): Metacritic ratings, OPTIONAL
            }

    Raises:
        None
    """
    assert type(movie_title) == str or type(movie_title) == unicode
    try:
        movie = tmdb3_search_by_title(movie_title)
    except Exception:
        pass

    try:
        if movie is None:
            movie = omdb_search_by_title(movie_title)
    except Exception:
        pass
    return movie


def movie_metadata_by_imdb_id(imdb_id):
    """Retrieve movie metadata by IMDb ID

    Searches for movies based on IMDb ID and retrieves their
    metadata from online sources. Uses TMDb as first choice,
    failing which OMDb is queried.

    Args:
        imdb_id(int): IMDb ID of the movie to be searched

    Returns:
        movie(dict): a dictionary containing the movie metadata
        or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
                metascore(int): Metacritic ratings, OPTIONAL
            }

    Raises:
        None
    """
    # assert type(imdb_id) == int
    try:
        movie = tmdb3_search_by_imdb_id(imdb_id)
    except Exception:
        pass
    try:
        movie2 = omdb_search_by_imdb_id(imdb_id)
    except Exception:
        pass
    if movie is not None:
        if movie2 is not None:
            movie['imdb_rating'] = movie2.get('imdb_rating', 0)
            movie['tomato_rating'] = movie2.get('tomato_rating', 0)
            movie['metascore'] = movie2.get('metascore', 0)
    else:
        if not movie2:
            movie = movie2
    return movie


def _omdb_url():
    """OMDb API url

    Provides the url to be used when querying OMDb for movie metadata.

    Args:
        None

    Returns:
        url(str): url of OMDb API
    """
    return 'http://www.omdbapi.com/?'


def omdb_search_by_title(movie_title):
    """Retrieve movie metadata by title through OMDb

    Searches for movies based on their title and retrieves their
    metadata from OMDb

    Args:
        movie_title(str): title of the movie to be searched

    Returns:
        movie(dict): a dictionary containing the movie metadata
        or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
                metascore(int): Metacritic ratings,
            }

    Raises:
        None
    """
    # print 'OMDb search: ', movie_title
    assert type(movie_title) == str or type(movie_title) == unicode
    url = _omdb_url()
    # all spaces in movie title should be replaced with '+' in OMDb
    url = ''.join([url, 's=', movie_title.replace(' ', '+')])
    # print url
    response = urllib2.urlopen(url, timeout=5)
    data = json.load(response)
    if data.get('Error', None):
        # data = {
        #     "Response":"False",
        #     "Error":"Movie not found!"
        # }
        return None
    # There is at least one result
    if data.get('Search', None):
        # multiple results
        return omdb_search_by_imdb_id(data['Search'][0]['imdbID'])
    elif data.get('Title', None):
        # single result
        return omdb_search_by_imdb_id(data['imdbID'])


def omdb_search_by_imdb_id(imdb_id):
    """Retrieve movie metadata by IMDb ID through OMDb

    Searches for movies based on IMDb ID and retrieves their
    metadata from OMDb.

    Args:
        imdb_id(int): IMDb ID of the movie to be searched
            or (str): prefixed with 'tt' and string length
            should be exactly 'tt' + xxxxxxx (7) digits

    Returns:
        movie(dict): a dictionary containing the movie metadata
        or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
                metascore(int): Metacritic ratings,
            }

    Raises:
        ValueError: invalid IMDb ID
    """
    # print 'OMDb search: ', imdb_id
    if type(imdb_id) == str or type(imdb_id) == unicode:
        # check for valid format
        pattern1 = re.compile(r'^tt[0-9]{7}$')
        pattern2 = re.compile(r'^[0-9]+$')
        if pattern2.match(imdb_id):
            imdb_id = 'tt' + imdb_id
        elif not pattern1.match(imdb_id):
            raise ValueError('Invalid IMDb ID ' + imdb_id)
    elif type(imdb_id) == int:
        imdb_id = 'tt' + '%07d' % imdb_id

    url = _omdb_url()
    # option tomatoes for retrieving RottenTomatoes ratings
    url = ''.join([url, 'i=', imdb_id, '&tomatoes=true'])
    # print url
    response = urllib2.urlopen(url, timeout=5)
    data = json.load(response)
    if data.get('Error', None):
        # data = {
        #     "Response":"False",
        #     "Error":"Movie not found!"
        # }
        return None
    return omdb_parse_result(data)


def omdb_parse_result(data):
    """Parse movie metadata retrieved from OMDb

    Parses the movie metadata retrieved from OMDb and converts it
    to a dictionary with some fields.

    Args:
        data(dict): JSON data downloaded from OMDb

    Returns:
        movie(dict): a dictionary containing the movie metadata
            or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
                metascore(int): Metacritic ratings,
            }

    Raises:
        None
    """
    # print 'omdb_parse'
    assert type(data) == dict
    movie = {}
    # TODO: Levenstein similarity of movie title and filename
    movie['title'] = data['Title']
    if data['Released'] != 'N/A':
        movie['release'] = datetime.strptime(data['Released'], '%d %b %Y')
    movie['imdb_id'] = int(data['imdbID'][2:])
    # list of actors
    if data['Actors'] != 'N/A':
        movie['cast'] = {
            'Actor': [
                actor.strip() for actor in data['Actors'].split(',')
            ],
        }
    # dictionary of lists of crew
    if data['Director'] != 'N/A':
        movie['crew'] = {
            'Director': [
                director.strip() for director in data['Director'].split(',')
            ],
        }
    if data.get('imdbRating', None):
        if data['imdbRating'] != 'N/A':
            movie['imdb_rating'] = float(data['imdbRating'])
        else:
            movie['imdb_rating'] = None
    if data.get('tomatoMeter', None):
        if data['tomatoMeter'] != 'N/A':
            movie['tomato_rating'] = int(data['tomatoMeter'])
    if data.get('Metascore', None):
        if data['Metascore'] != 'N/A':
            movie['metascore'] = int(data['Metascore'])
    return movie


def tmdb3_search_by_title(movie_title):
    """Retrieve movie metadata by title through TMDb

    Searches for movies based on their title and retrieves their
    metadata from TMDb.

    Args:
        movie_title(str): title of the movie to be searched

    Returns:
        movie(dict): a dictionary containing the movie metadata
        or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
            }

    Raises:
        None
    """
    try:
        # print 'TMDb: ', movie_title
        # log('downloading movie metadata...', newline=False)
        res = searchMovie(movie_title)
        assert res is not None
        if len(res) == 0:
            # no match found
            print 'TMDb not found: ', movie_title
            return
        # log('COMPLETE!')
        if len(res) == 1:
            # got our movie!!!
            res = res[0]
        else:
            # TODO: offer user the choice of movies
            res = res[0]
        movie = tmdb_parse_result(res)
        return movie
    except Exception as e:
        print movie_title, "TMDb(T): Error retrieving movie metadata!"
        print "TMDb(T): ", e


def tmdb3_search_by_imdb_id(imdb_id):
    """Retrieve movie metadata by IMDb ID through TMDb

    Searches for movies based on IMDb ID and retrieves their
    metadata from TMDb.

    Args:
        imdb_id(int): IMDb ID of the movie to be searched

    Returns:
        movie(dict): a dictionary containing the movie metadata
        or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
            }


    Raises:
        None
    """
    try:
        # print 'TMDb(I):' + str(imdb_id)
        if type(imdb_id) == str or type(imdb_id) == unicode:
            # check for valid format
            pattern1 = re.compile(r'^tt[0-9]{7}$')
            pattern2 = re.compile(r'^tt[0-9]+$')
            pattern3 = re.compile(r'^[0-9]+$')
            if pattern1.match(imdb_id):
                # print 'TMDb(P1): ' + imdb_id
                pass
            elif pattern2.match(imdb_id):
                imdb_id = 'tt' + '%07d' % int(imdb_id[2:])
                # print 'TMDb(P2): ' + imdb_id
            elif pattern3.match(imdb_id):
                imdb_id = 'tt' + '%07d' % int(imdb_id)
                # print 'TMDb(P3): ' + imdb_id
            else:
                raise ValueError('Invalid IMDb ID ' + imdb_id)
        elif type(imdb_id) == int:
            imdb_id = 'tt' + '%07d' % imdb_id
        # print 'TMDb: ', imdb_id
        # log('downloading movie metadata...', newline=False)
        res = tmdbMovie.fromIMDB(imdb_id)
        if res is not None:
            movie = tmdb_parse_result(res)
            return movie
    except KeyError as e:
        print imdb_id, ' TMDb: IMDb ID does not match any known movie.'
        print e
        return
    # log('COMPLETE!')
    except Exception as e:
        print imdb_id, "TMDb(I): Error retrieving movie metadata!"
        print "TMDb(I): ", e


def tmdb_parse_result(res):
    """Parse movie metadata retrieved from TMDb

    Parses the movie metadata retrieved from OMDb and converts it
    to a dictionary with some fields.

    Args:
        res(dict): JSON data downloaded from TMDb

    Returns:
        movie(dict): a dictionary containing the movie metadata
            or None otherwise
            movie {
                title(str): movie title,
                release(datetime): movie release date/time,
                imdb_id(int): IMDb ID of the movie,
                cast(dict): movie cast {
                    'Actor'(list): list of actors in movie,
                },
                crew(dict): movie crew {
                    'Director'(list): list of movie directors,
                },
                imdb_rating(float): IMDb rating for this movie,
                tomato_rating(int): RottenTomatoes ratings,
            }

    Raises:
        None
    """
    # log('starting to parse metadata...')
    movie = {}
    movie['title'] = res.title
    movie['release'] = res.releasedate
    # list of actors
    movie['cast'] = tmdb_result_cast(res)
    # dictionary of lists of crew
    movie['crew'] = tmdb_result_crew(res)
    movie['imdb_rating'] = imdb_rating_by_id(res.imdb)
    movie['tomato_rating'] = tomato_rating_by_imdb_id(res.imdb)
    return movie


def tmdb_result_cast(res):
    """Parse movie cast from TMDb result

    Parses the movie cast metadata retrieved from TMDb and converts it
    to a dictionary with some fields.

    Args:
        res(dict): JSON data downloaded from TMDb

    Returns:
        cast(dict): a dictionary containing the movie metadata
            cast {
                Actor(list): list of actors,
            }

    Raises:
        None
    """
    # log('getting cast...', newline=False)
    cast = {}
    actors = []
    for actor in res.cast:
        actors.append(actor.name)
    cast['Actor'] = actors
    # log('COMPLETE. ' + str(len(cast)) + ' actors retrieved.')
    return cast


def tmdb_result_crew(res):
    """Parse movie crew from TMDb result

    Parses the movie crew metadata retrieved from TMDb and converts it
    to a dictionary with some fields.

    Args:
        res(dict): JSON data downloaded from TMDb

    Returns:
        crew(dict): a dictionary containing the movie metadata
            crew {
                Director(list): list of directors,
            }

    Raises:
        None
    """
    # log('getting crew... ', newline=False)
    crew = {
        'Director': [],
    }

    for c in res.crew:
        if c.job in crew:
            crew[c.job].append(c.name)
            # log(c.name + '-' + c.job, level=LOGGING_LEVELS['TRACE'])
    # log('COMPLETE.')
    return crew


def imdb_rating_by_id(imdb_id):
    """Retrieve IMDb rating by IMDb ID

    Retrieves the rating for a movie based on the given imdb id.

    Args:
        imdb_id(int): IMDb ID for given movie

    Returns:
        rating(float): IMDb rating for given ID

    Raises:
        None
    """
    # log('retrieving IMDb rating...', newline=False)
    rating = json.load(urllib2.urlopen(
        'http://app.imdb.com/title/maindetails?tconst=' +
        str(imdb_id)))['data']['rating']
    # log(rating)
    return rating


def tomato_rating_by_imdb_id(imdb_id):
    """Retrieve RottenTomatoes rating by IMDb ID

    Retrieves the RT rating for a movie based on the given imdb id.

    Args:
        imdb_id(int): IMDb ID for given movie

    Returns:
        rating(int): RottenTomatoes rating for given ID

    Raises:
        None
    """
    # log('retrieving Rotten Tomatoes rating... API inactive')
    # TODO: activate when RT api use is approved
    rating = 0
    '''json.load(urllib2.urlopen('
        http://api.rottentomatoes.com/api/public/v1.0/movie_alias.json?
        apikey=taj5ecgq5extfg9tq93f93x5&
        type=imdb&id=' + str(imdb_id)))['ratings']['critics_score']'''

    return rating


def start_loader():
    """Start the loader

    Starts the loader after checking hdd and movie folder are accessible.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    hdd_root = HDDRoot.get_solo().path
    if not path.exists(hdd_root):
        print _ERROR[1]
        return _ERROR[1]
    movie_folder = MovieFolder.get_solo().relpath
    if not path.exists(path.join(hdd_root, movie_folder)):
        print _ERROR[1]
        return _ERROR[2]
    loader_status('STATUS', True)
    thread = Thread(target=_run)
    thread.daemon = True
    thread.start()


def stop_loader():
    """Stop the loader

    Stops the loader.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    loader_status('STATUS', False)
