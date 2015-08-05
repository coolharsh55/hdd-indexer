"""Download movie metadata from online sources

    The load module uses OpenSubtitles to try and identify movie
    and get it's IMDb ID. If this cannot be retrieved, it uses
    the filename to perform a movie_title search using external API.
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

from os import path
from datetime import datetime
import json
import Queue
from threading import Thread
from threading import Lock
import urllib2
import re
from xmlrpclib import ProtocolError
import logging
import traceback

from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
import tmdbsimple as tmdb

from hdd_settings.models import HDDRoot
from hdd_settings.models import MovieFolder
from movie_metadata.models import Movie
from hdd_settings.models import TMDbKey
from hdd_settings.models import OpenSubKey
from movie_metadata.movie import save as movie_save


_ERROR = {
    1: 'HDD Root not configured properly.',
    2: 'Movie Folder not configured properly.',
}
"""Crawler Error messages
"""

log = logging.getLogger('load')
log.info(72 * '-')
log.info("load module loaded")


def loader_status(key=None, value=None):
    """Loader status

    Args:
        key(dict key): key to search in dict
        value(dict value): value to assign to key

    Returns:
        status(bool): True for ON, False for OFF

    """
    if 'status' not in loader_status.__dict__:
        loader_status.lock = Lock()
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
            if key == 'SKIPPED_LIST':
                with loader_status.lock:
                    _LOADER['SKIPPED_LIST'].append(value)
                log.debug('%s added to skipped list' % value)
            else:
                with loader_status.lock:
                    _LOADER[key] = value
                log.debug('status: %s -> %s' % (key, value))
        else:
            return _LOADER[key]
    return _LOADER['STATUS']


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
    # TODO: wrap the entire func in try block
    tmdb.API_KEY = TMDbKey.get_solo().key
    t_size = 5  # size of thread, and movie queue
    # download job queue
    q = Queue.LifoQueue()
    # movies to be saved to database
    m = Queue.Queue()
    # skipped movies
    movies = list(Movie.objects.all())
    log.info('started load run with %s movies' % len(movies))
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
            log.debug('%s queued' % movie.title)
            q.put(movie)

        log.debug('starting %s threads' % t_size)
        for i in range(t_size):
            # start threads
            thread = Thread(target=_load, args=(q, m))
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
                log.info('%s saved to database' % data['title'])
            except Exception:
                log.error('error saving %s to database.' % data['title'])
                log.error(traceback.format_exc())
                loader_status('SKIPPED', movie.title)
                log.debug('%s put in skipped list' % movie.title)
                # movie.save()
            m.task_done()

        log.info('%s items processed of %s' % (
            len(m_list) + m_start, len(movies)
        ))
        m_start += t_size
        m_list = movies[m_start:m_start + t_size]

    loader_status('STATUS', False)


def _load(q, m):
    """Load metadata from online sources

    Gets a movie from the job q,
    Downloads JSON from online, parses it,
    and saves it to the movie save queue m.

    Args:
        q(Queue): movie object queue to be processed
        m(Queue): movie object queue to be saved

    Returns:
        None

    Raises:
        None
    """
    while not q.empty():
        if not loader_status('STATUS'):
            # loader has been turned off
            log.info('loader turned off, dumping movies in queue')
            while not q.empty():
                movie = q.get()
                log.info('%s dumped' % movie.title)
                q.task_done()
            return
        # get a movie object from q
        movie = q.get()
        log.debug('processing movie: %s' % movie.title)

        data = None
        if movie.imdb_id is not None:
            # get metadata by imdb id
            log.debug('movie: %s by imdb id: %s' % (
                movie.title, movie.imdb_id)
            )
            data = movie_metadata_by_imdb_id(movie.imdb_id)
        if data is None:
            # get metadata by title (or filename)
            # can also mean imdb id is not available
            log.debug('movie: %s by title' % movie.title)
            data = movie_metadata_by_title(movie.title)
        if data is not None:
            # movie has metadata
            data['relpath'] = movie.relpath
            log.info('movie: %s metadata received' % movie.title)
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
                log.warning('movie: %s skipped' % movie.title)
                loader_status(
                    'MOVIES_EVALUATED',
                    loader_status('MOVIES_EVALUATED') + 1
                )
                loader_status(
                    'MOVIES_SKIPPED',
                    loader_status('MOVIES_SKIPPED') + 1
                )
                loader_status('SKIPPED_LIST', movie.title)

            else:
                # opensub identified movie
                movie.imdb_id = imdb_id
                log.info('movie: %s got opensub imdb id: %s' % (
                    movie.title, movie.imdb_id
                ))
                # put it back in the queue to download its metadata
                # the next time a thread retrieves it
                q.put(movie)
        q.task_done()


def opensub_initiate():
    """OpenSubtitles initiation for use

    Login to OpenSubtitles using API to retrieve a token
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
    try:
        # login to opensub using API
        sub = OpenSubtitles()
        token = sub.login(OpenSubKey.get_solo().uid, OpenSubKey.get_solo().key)
        if not token:
            # return sub
            print 'null token'
            log.error('open sub null token')
            return
        return sub
    except ProtocolError as e:
        # most likely network error or API server error
        print "E: " + str(e)
    except AssertionError:
        print 'Failed to authenticate opensubtitles login.'
    except ProtocolError as e:
        """
        TODO: gaierror:
            [Errno 8] nodename nor servname provided, or not known
        """
        if e.errcode == 503:
            # ProtocolError - 503 Service Unavailable
            print 'Check network connection and try again.'
        log.error('open sub error occured')
        log.error(traceback.format_exc())
    except Exception:
        log.error('open sub error occured')
        log.error(traceback.format_exc())


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
    if 'sub' not in opensub.__dict__:
        with Lock():
            sub = opensub_initiate()
            if sub:
                opensub.sub = sub

    sub = opensub.sub
    try:
        # login to opensub using API
        token = sub.login(OpenSubKey.get_solo().uid, OpenSubKey.get_solo().key)
        if not token:
            # return sub
            print 'null token'
            log.error('path: %s open sub null token' % relpath)
            return
        # check that the file is accessible
        if not path.exists(path.join(
            HDDRoot.get_solo().path,
            MovieFolder.get_solo().relpath,
            relpath,
        )):
            print "ERROR: " + relpath
            log.error('path: %s does not exist' % relpath)
            return
        f = File(path.join(
            HDDRoot.get_solo().path,
            MovieFolder.get_solo().relpath,
            relpath,
        ))
        if f is None:
            log.error('path: %s open sub file error' % relpath)
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
        else:
            log.warning('%s opensub failed to identify movie' % relpath)
    except ProtocolError as e:
        # most likely network error or API server error
        print "E: " + str(e)
    except AssertionError:
        print 'Failed to authenticate opensubtitles login.'
    except ProtocolError as e:
        """
        TODO: gaierror:
            [Errno 8] nodename nor servname provided, or not known
        """
        if e.errcode == 503:
            # ProtocolError - 503 Service Unavailable
            print 'Check network connection and try again.'
        log.error('path: %s open sub error occured' % relpath)
        log.error(traceback.format_exc())
    except Exception:
        log.error('path: %s open sub error occured' % relpath)
        log.error(traceback.format_exc())


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
        # if movie is None:
        #     movie = omdb_search_by_title(movie_title)
        return movie
    except Exception:
        pass
    return


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
    try:
        movie = omdb_search_by_imdb_id(imdb_id)
        if movie is None:
            movie = tmdb3_search_by_imdb_id(imdb_id)
        return movie
    except Exception:
        pass


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
    log.debug('movie: %s omdb %s' % (movie_title, url))
    response = urllib2.urlopen(url, timeout=5)
    data = json.load(response)
    if data.get('Error', None):
        # data = {
        #     "Response":"False",
        #     "Error":"Movie not found!"
        # }
        log.warning('movie: %s omdb found no results' % movie_title)
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
    print 'OMDb search: ', imdb_id
    if type(imdb_id) == str or type(imdb_id) == unicode:
        # check for valid format
        pattern1 = re.compile(r'^tt[0-9]{7}$')
        pattern2 = re.compile(r'^[0-9]+$')
        if pattern2.match(imdb_id):
            imdb_id = 'tt' + '%07d' % int(imdb_id)
        elif not pattern1.match(imdb_id):
            raise ValueError('Invalid IMDb ID ' + imdb_id)
    elif type(imdb_id) == int:
        imdb_id = 'tt' + '%07d' % imdb_id

    url = _omdb_url()
    # option tomatoes for retrieving RottenTomatoes ratings
    url = ''.join([url, 'i=', imdb_id, '&tomatoes=true'])
    log.debug('imdb_id: %s omdb search %s' % (imdb_id, url))
    response = urllib2.urlopen(url, timeout=5)
    data = json.load(response)
    if data.get('Error', None):
        # data = {
        #     "Response":"False",
        #     "Error":"Movie not found!"
        # }
        log.warning('imdb_id: %s omdb found no results' % imdb_id)
        return None
    log.debug('%s omdb found results' % imdb_id)
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
    print 'omdb_parse: %s' % data['Title']
    assert type(data) == dict
    movie = {}
    # TODO: Levenstein similarity of movie title and filename
    movie['title'] = data['Title']
    if data['Released'] != 'N/A':
        movie['release'] = datetime.strptime(data['Released'], '%d %b %Y')
    movie['imdb_id'] = int(data['imdbID'][2:])
    log.info('omdb found %s %s' % (movie['title'], movie['imdb_id']))
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
        print 'TMDb: ', movie_title
        search = tmdb.Search()
        response = search.movie(query=movie_title)
        if response['total_results'] == 0:
            # no match found
            log.warning('movie: %s tmdb no results' % movie_title)
            print 'TMDb not found: ', movie_title
            return

        # TODO: offer user the choice of movies
        # search.results -> select

        # we have a title, now do an OMDb search by title
        # because TMDb does not support getting imdb ID
        response = tmdb.Movies(search.results[0]['id'])
        imdb_id = tmdb.Movies(search.results[0]['id']).info()['imdb_id']
        log.info('movie: %s %s found by tmdb' % (
            search.results[0]['title'], imdb_id
        ))
        movie = omdb_search_by_imdb_id(imdb_id)
        if movie is None:
            # omdb could not get metadata
            # save whatever information we have to database
            movie = tmdb_parse_result(search.results[0])
            response = tmdb.Movies(search.results[0]['id'])
            movie.imdb_id = response.info()['imdb_id']
            movie.imdb_rating = imdb_rating_by_id(movie.imdb_id)
        return movie
    except Exception:
        print movie_title, "TMDb(T): Error retrieving movie metadata!"
        print "TMDb(%s): error occured" % movie_title
        log.error(traceback.format_exc())


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
        print 'TMDb: %s' % imdb_id
        # log('downloading movie metadata...', newline=False)
        url = 'https://api.themoviedb.org/3/find/%s' \
            '?external_source=imdb_id&api_key=%s' % \
            (imdb_id, TMDbKey.get_solo().key)
        log.debug('%s tmdb by imdb id %s' % (imdb_id, url))
        res = json.load(urllib2.urlopen(url, timeout=5))
        if res is not None:
            movie = tmdb_parse_result(res['movie_results'][0])
            movie['imdb_id'] = imdb_id
            movie['imdb_rating'] = imdb_rating_by_id(imdb_id)
            return movie
    except KeyError as e:
        print imdb_id, ' TMDb: IMDb ID does not match any known movie.'
        print e
    # log('COMPLETE!')
    except Exception:
        print "TMDb(I): %s Error retrieving movie metadata!" % imdb_id
        log.error("TMDb(%s): %s" % (imdb_id, traceback.format_exc()))


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
    movie['title'] = res['title']
    movie['release'] = datetime.strptime(res['release_date'], '%Y-%m-%d')
    log.info('movie: %s tmdb result' % movie['title'])
    # # list of actors
    # movie['cast'] = tmdb_result_cast(res)
    # # dictionary of lists of crew
    # movie['crew'] = tmdb_result_crew(res)
    # movie['imdb_rating'] = imdb_rating_by_id(res.imdb)
    # movie['tomato_rating'] = tomato_rating_by_imdb_id(res.imdb)
    return movie


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
