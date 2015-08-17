"""organizer

organize movies by:
    release date:
        current decade - by year: 2015, 2014, 2013...
        previous decards - by decade: 2000, 1990, 1980
    imdb rating:
        5.0 and below
        7.0 and below
        7.5, 8.0, 8.5 ... (0.5 increments)
"""

# TODO: propogate error to browser if thread fails

from datetime import datetime
from math import floor
from ntpath import splitext
from os import makedirs
from os import path
from os import walk
from shutil import move
from shutil import rmtree
from threading import Thread

from hdd_settings.models import HDDRoot
from hdd_settings.models import MovieFolder
from movie_metadata.models import Movie

import logging
log = logging.getLogger('organize')
log.info(72 * '-')
log.info('organize module loaded')


def organizer_status(key=None, value=None):
    """Organizer status

    Args:
        key(dict key): key to search in dict
        value(dict value): value to assign to key

    Returns:
        bool: True for ON, False for OFF
    """
    if 'status' not in organizer_status.__dict__:
        organizer_status.status = {
            'STATUS': False,
            'FILES_EVALUATED': 0,
        }
    _ORGANIZER = organizer_status.status
    if _ORGANIZER.get(key) is not None:
        if value is not None:
            log.info('organizer status: %s -> %s' % (key, value))
            # TODO: check if key and value are valid
            _ORGANIZER[key] = value
        else:
            return _ORGANIZER[key]
    return _ORGANIZER['STATUS']


def make_fname(title, relpath):
        """creates a new filename for the movie from its title

        Uses the movie title saved in database along with the original
        file extension to create a new and correct filename

        Args:
            title(str): title of the movie
            relpath(str): path stored in database

        Returns:
            str: new filename.ext

        Raises:
            None
        """
        # TODO: validate relpath contains filename.ext
        extension = splitext(relpath)[1]
        # TODO: validate that this is a valid/legal filename
        return title + extension


def _criterion_tools(criterion):
    """select the organization criteria

    Attaches functions based on user choice for organization criterion.
    Supported criterions are: release date, imdb score

    Args:
        criterion(str): choice selected by user

    Returns:
        None

    Raises:
        ValueError: invalid criterion
    """
    assert type(criterion) == str or type(criterion) == unicode
    log.info('organization criterion: %s' % criterion)
    if criterion == 'release':
        _get_folder = _folder_by_release_date
        _field_exists = lambda m: m.release is not None
    elif criterion == 'imdb_score':
        _get_folder = _folder_by_imdb_score
        _field_exists = lambda m: m.imdb_score is not None
    else:
        raise ValueError('Invalid organization criterion: %s' % criterion)
    return _get_folder, _field_exists


def _organize(criterion):
    """organize movies on disk/database by provided criterion

    Selects all movies and updates their filenames based on their
    metadata titles. Moves their files to organized folders whose
    name and hierarchy are based on criterion selected.

    Args:
        criterion(str): user choice of organization criterion

    Returns:
        None

    Raises:
        None
    """
    def create_folder(folder):
        """ creates a folder if it does not exist

        Args:
            folder(str): path of the folder

        Returns:
            None

        Raises:
            None
        """
        # TODO: check if path is valid
        if not path.exists(path.join(destination, folder)):
            log.info('created directory %s' % folder)
            makedirs(path.join(destination, folder))

    # functions for selected criterion
    _get_folder, _field_exists = _criterion_tools(criterion)
    # temporary folder for holding created folders
    tempname = 'tmp'
    log.debug('temporary folder set to ./%s' % tempname)
    uncategorized = 'uncategorized'
    log.debug('uncategorized folder set to ./%s/%s' % (
        tempname, uncategorized))
    parentpath = path.join(
        HDDRoot.get_solo().path,
        MovieFolder.get_solo().relpath)
    destination = path.join(parentpath, tempname)
    create_folder(destination)

    movies = Movie.objects.all()
    for movie in movies:

        # parent folder for the movie file
        if _field_exists(movie):
            folder = _get_folder(movie)
        else:
            folder = uncategorized
        log.debug('folder: %s' % folder)
        create_folder(folder)

        # create new filename -> title with extension
        fname = make_fname(movie.title, movie.relpath)
        # move the file to its new location
        newpath = path.join(
            path.join(destination, folder),
            fname)
        oldpath = path.join(parentpath, movie.relpath)
        move(oldpath, newpath)
        log.debug('%s moved from %s to %s' % (
            movie.title, movie.relpath, newpath))
        # update movie path to the newpath
        movie.relpath = path.join(folder, fname)
        # save updated movie to database
        movie.save()

    # move other files from movie_folder to new folder
    other_files = path.join(destination, 'other_files')
    create_folder(other_files)
    for root, directory, files in walk(parentpath):
        # don't go into the temporary folder
        if not root.startswith(destination):
            for somefile in files:
                move(
                    path.join(root, somefile),
                    path.join(other_files, somefile))
    log.info('moved other files into %s' % other_files)

    # remove all directories from movie folder
    for directory in walk(parentpath).next()[1]:
        if directory != tempname:
            rmtree(path.join(parentpath, directory))
    log.info('removed all directories from movie folder')

    # move all new folders into movie folder directory
    for directory in walk(destination).next()[1]:
        move(
            path.join(destination, directory),
            path.join(parentpath, directory))

    # delete temporary directory
    rmtree(destination)

    # update status of organizer
    organizer_status('STATUS', False)


def _folder_by_release_date(movie):
    """identifies the correct folder from movie release date

    If the movie's release date is in the current decade, it assigns
    the release year as its folder name. Otherwise, the decade year
    is assigned as its folder name.
    E.g. release dates in 2015 (now) will be stored in '2015'
    release dates (2001, 2006, ...) will be stored in '2000'

    Args:
        movie(Movie): movie object from database

    Returns:
        str: foldername for the movie file

    Raises:
        None
    """
    # TODO: check if movie is a valid Movie object
    # TODO: check if movie has a valid release date
    if 'this_decade' not in _folder_by_release_date.__dict__:
        _folder_by_release_date.this_decade = \
            datetime.now().year - datetime.now().year % 10
    if 'get_decade' not in _folder_by_release_date.__dict__:
        _folder_by_release_date.get_decade = lambda year: year - year % 10
    if movie.release.year < _folder_by_release_date.this_decade:
        folder = _folder_by_release_date.get_decade(movie.release.year)
    else:
        folder = movie.release.year
    return str(folder)


def _folder_by_imdb_score(movie):
    """identifies the correct folder from movie score

    If the movie's score is below a certain threshold, dumps all such
    movies together. Otherwise saves each movie in folder based on
    IMDb score with 0.5 incrememnts.
    For e.g. movie with score 4.5, 3.2, ... go into 'below 5.0'
    movie with score 5.1, 6.2, 6.9, ... go into 'below 7.0'
    movie with score 7.3 go into '7.0', 7.8 go into '7.5'

    Args:
        movie(Movie): movie object from database

    Returns:
        str: foldername for movie file

    Raises:
        None
    """
    imdb_score = movie.imdb_score
    # movies rated 5.0 and below
    if imdb_score < 5.0:
        folder = 'below 5.0'
    # movies rated 7.0 and below
    elif imdb_score < 7.0:
        folder = 'below 7.0'
    else:
        # 8.2 -> 8.2 + 0.5 -> floor(8.7) -> 8.0 -> 8.0
        # 8.7 -> 8.7 + 0.5 -> floot(9.2) -> 9.0 -> 8.5
        base = floor(imdb_score + 0.5)
        # movie is rated something like x.y
        if imdb_score < base:
            # y > 0.5, e.g. score:8.7 -> folder:8.5
            folder = str(base - 0.5) + ' and above'
        else:
            # y < 0.5 e.g. score:8.2 -> folder:8.0
            folder = str(base) + ' and above'
    return folder


def start_organizer(criterion='release'):
    """Start the organizer

    Args:
        criterion(str): specifies organization structure

    Returns:
        None

    Raises:
        None
    """
    log.info('Started organizer with criterion: %s' % criterion)
    thread = Thread(target=_organize, args=(criterion, ))
    thread.daemon = True
    thread.start()
    log.info('organizer started on daemon thread')
    organizer_status('STATUS', True)


def stop_organizer():
    """Stop the organizer

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    log.info('Stopped organizer')
    organizer_status('STATUS', False)
