"""Views for hdd-indexer

    / - homepage
    /crawler [GET/POST] - crawler interactions
    /loader [GET/POST] - loader interactions
    /settings [POST] - settings
    /setup [POST] - setup

"""

# TODO: refactor validations into separate methods
# TODO: make validation a method of class
# HDDRoot.validate(path): True on success, False otherwise
# if True, assigns the path to HDDRoot.path
# then we need to call HDDRoot.save() to save the path
# TODO: check if crawler/loader active and send status to homepage


import json
from os import path
import re
import logging
log = logging.getLogger('server')
log.info(72*'-')
log.info('server views loaded')

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from hdd_settings.models import RegistrationKey
from hdd_settings.models import HDDName
from hdd_settings.models import HDDRoot
from hdd_settings.models import MovieFolder
from hdd_settings.models import TMDbKey
from hdd_settings.models import OpenSubKey
from setup import internet_on

from movie_metadata.crawl import crawler_status
from movie_metadata.crawl import start_crawler
from movie_metadata.crawl import stop_crawler

from movie_metadata.load import loader_status
from movie_metadata.load import start_loader
from movie_metadata.load import stop_loader


@csrf_exempt
def crawler(request):
    """crawler interactions on /crawler for hdd-indexer

    Interactions with crawler using GET and POST

    GET:
        status(str): status of crawler ON/OFF

    POST:
        start(str): start the crawler
        stop(str): stop the crawler

    Args:
        request(RequestContext) - passed by Django

    Returns:
        response(HttpResponse) - resposne to GET/POST request

    Raises:
        None
    """

    def response(e_m=None):
        """Response for GET/POST methods on crawler

        returns a HTTPResponse with content type json

        Args:
            e_m(str): error message if any
            e_m(None): if no error message
        """
        if e_m:
            e = True
        else:
            e = False
        payload = {
            'status': crawler_status(),
            'files_evaluated': crawler_status('FILES_EVALUATED'),
            'movies_found': crawler_status('MOVIES_FOUND'),
            'movies_added': crawler_status('MOVIES_ADDED'),
            'error': e,
            'error_message': e_m,
        }
        log.debug('crawler status: %s' % payload)
        return HttpResponse(
            json.dumps(payload),
            content_type='application/json'
        )

    # if request is not POST, return error
    if request.method == 'GET':
        # print 'GET', request.GET
        if request.GET.get('status', None):
            log.debug('GET: crawler status')
            return response()
    elif request.method == 'POST':
        # print 'POST', request.POST
        if request.POST.get('start', None):
            log.info('POST: start crawler')
            err_msg = start_crawler()
            if err_msg:
                log.error('start crawler: %s' % err_msg)
                return response(err_msg)
            return response()
        elif request.POST.get('stop', None):
            log.info('POST: stop crawler')
            err_msg = stop_crawler()
            if err_msg:
                log.error('stop crawler: %s' % err_msg)
                return response(err_msg)
            return response()

    # 405: Method not allowed
    log.error('405: method not allowed')
    return HttpResponse(status=405)


@csrf_exempt
def help(request):
    """Help for HDD-indexer

    Shows the help page containing help on modules and settings

    Args:
        request(HttpRequest): request to server

    Returns:
        render(HttpResponse): shows the help page

    Raises:
        None
    """
    log.debug('help.html served with welcome=False')
    return render(
        request,
        'hdd_indexer/help.html',
        {
            'welcome': False,
        }
    )


@csrf_exempt
def loader(request):
    """crawler interactions on /loader for hdd-indexer

    Interactions with loader using GET and POST

    GET:
        status(str): status of loader ON/OFF

    POST:
        start(str): start the loader
        stop(str): stop the loader

    Args:
        request(RequestContext) - passed by Django

    Returns:
        response(HttpResponse) - resposne to GET/POST request

    Raises:
        None
    """

    def response(e_m=None):
        """Response for GET/POST methods on loader

        returns a HTTPResponse with content type json

        Args:
            e_m(str): error message if any
            e_m(None): if no error message
        """
        if e_m:
            e = True
        else:
            e = False
        # print loader_status('SKIPPED_LIST')
        payload = {
            'status': loader_status(),
            'movies_evaluated': loader_status('MOVIES_EVALUATED'),
            'metadata_downloaded': loader_status('METADATA_DOWNLOADED'),
            'movies_skipped': loader_status('MOVIES_SKIPPED'),
            'skipped_list': loader_status('SKIPPED_LIST'),
            'error': e,
            'error_message': e_m,
        }
        log.debug('loader status: %s' % payload)
        # print payload
        return HttpResponse(
            json.dumps(payload),
            content_type='application/json'
        )

    # if request is not POST, return error
    if request.method == 'GET':
        # print 'GET', request.GET
        if request.GET.get('status', None):
            log.debug('GET: loader status')
            return response()
    elif request.method == 'POST':
        # print 'POST', request.POST
        if request.POST.get('start', None):
            log.info('POST: start loader')
            if not internet_on():
                log.warning('Start Loader: No Internet Connectivity')
                return response('Please check your Internet connection!!!')
            # print 'starting loader'
            err_msg = start_loader()
            if err_msg:
                log.error('start loader: %s' % err_msg)
                return response(err_msg)
            # print 'started loader'
            return response()
        elif request.POST.get('stop', None):
            log.info('POST: stop loader')
            err_msg = stop_loader()
            if err_msg:
                log.error('stop loader: %s' % err_msg)
                return response(err_msg)
            return response()

    # 405: Method not allowed
    log.error('405: Method not allowed')
    return HttpResponse(status=405)


def homepage(request):
    """homepage view for / on hdd-indexer

    Serves the homepage at root (/) with index.html
    Passes hdd_name, hdd_root, movie_folder, crawler_status

    Args:
        request(RequestContext) - passed by Django

    Returns:
        response(Response) - file template to serve

    Raises:
        None
    """
    log.info('served homepage')
    return render(
        request,
        'hdd_indexer/index.html',
        {
            'hdd_name': HDDName.get_solo(),
            'hdd_root': HDDRoot.get_solo(),
            'movie_folder': path.join(
                HDDRoot.get_solo().path,
                MovieFolder.get_solo().relpath,
            ),
            'crawler_status': crawler_status(),
        }
    )


@csrf_exempt
def settings(request):
    """settings view for / on hdd-indexer

    Validates settings sent using POST

    POST:
        hdd_name(str)
        hdd_root(str)
        movie_folder(str)

    Args:
        request(RequestContext) - passed by Django

    Returns:
        response(HttpResponse) - resposne to POST request

    Raises:
        None
    """

    def response(d=True, v=True):
        """Response for POST methods

        returns a HTTPResponse with content type json

        Args:
            d(bool): POST success (JQuery done)
            v(bool): POST validation
        """
        payload = {
            'done': d,
            'validation': v,
        }
        log.debug('settings validation: %s' % payload)
        return HttpResponse(
            json.dumps(payload),
            content_type='application/json'
        )

    # if request is not POST, return error
    if request.method != 'POST':
        # 405: Method not allowed
        log.error('405: Method not allowed')
        return HttpResponse(status=405)

    # request for HDD Name
    if request.POST.get('hdd_name', None):
        hdd_name = request.POST['hdd_name']
        log.info('POST: hdd_name: %s' % hdd_name)
        pattern = re.compile(r'^[0-9a-zA-z_-]+$')
        if pattern.match(hdd_name):
            try:
                hdd_name_db = HDDName.get_solo()
                hdd_name_db.name = hdd_name
                hdd_name_db.save()
                log.info('hdd_name = %s saved to db' % hdd_name)
                return response()
            except ValueError:
                return response(d=False, v=True)
            except TypeError:
                return response(d=False, v=False)
            except Exception as e:
                print e
                return response(d=False, v=False)
        else:
            log.error('%s is a not a valid hdd_name' % hdd_name)
            return response(d=False, v=True)

    # request for HDD Root
    elif request.POST.get('hdd_root', None):
        hdd_root = request.POST['hdd_root']
        log.info('POST: hdd_root = %s' % hdd_root)
        if path.isdir(hdd_root):
            hdd_root_db = HDDRoot.get_solo()
            hdd_root_db.path = hdd_root
            hdd_root_db.save()
            log.info('hdd_root = %s saved to db' % hdd_root)
            return response()
        else:
            log.error('%s is not a valid path' % hdd_root)
            return response(d=False, v=True)

    # request for Movie Folder
    elif request.POST.get('movie_folder', None):
        movie_folder = request.POST['movie_folder']
        log.info('POST: movie_folder = %s' % movie_folder)
        hdd_root = HDDRoot.get_solo().path
        if not movie_folder.startswith(hdd_root):
            log.error('movie_folder does not start with hdd_root')
            return response(d=False, v=True)
        if not path.isdir(movie_folder):
            log.error('movie_folder is not a valid path')
            return response(d=False, v=True)
        movie_folder = path.relpath(movie_folder, hdd_root)
        movie_folder_db = MovieFolder.get_solo()
        movie_folder_db.relpath = movie_folder
        movie_folder_db.save()
        log.info('movie_folder = %s saved to db' % movie_folder)
        return response(d=True)

    log.error('405: Method not allowed')
    return HttpResponse(status=405)


@csrf_exempt
def setup(request):
    """Setup for first-use
    """
    if not request.POST:
        log.info('served setup page')
        return render(
            request,
            'hdd_indexer/setup.html',
            {
                'RegistrationKey': RegistrationKey.get_solo().key,
                'hdd_name': HDDName.get_solo().name,
                'hdd_root': HDDRoot.get_solo().path,
                'movie_folder': MovieFolder.get_solo().relpath,
                'opensub_id': OpenSubKey.get_solo().uid,
                'opensub_key': OpenSubKey.get_solo().key,
                'tmdb_key': TMDbKey.get_solo().key,
                'error': False,
                'err_msg': '',
            }
        )

    error = False
    err_msg = 'Validation errors have been found: '
    log.info('POST: preferences and settings in setup')
    # validations
    # registration key
    registration_key = request.POST.get('ID', '')
    if registration_key:
        # make sure that it is valid registration key
        registration_key_db = RegistrationKey.get_solo()
        registration_key_db.key = registration_key
        registration_key_db.save()
        log.info('registration key = %s saved to db' % registration_key)
    else:
        pass

    # hdd name
    hdd_name = request.POST.get('HDDName', '')
    pattern = re.compile(r'^[0-9a-zA-z_-]+$')
    if pattern.match(hdd_name):
        hdd_name_db = HDDName.get_solo()
        hdd_name_db.name = hdd_name
        hdd_name_db.save()
        log.info('hdd_name: %s saved to db' % hdd_name)
    else:
        error = True
        err_msg = ' '.join(((err_msg, 'HDD Name,')))
        log.error('%s is not a valid hdd_name' % hdd_name)

    # hdd root
    hdd_root = request.POST.get('HDDRoot', '')
    if path.exists(hdd_root):
        hdd_root_db = HDDRoot.get_solo()
        hdd_root_db.path = hdd_root
        hdd_root_db.save()
        log.info('hdd_root = %s saved to db' % hdd_root)
    else:
        error = True
        err_msg = ' '.join(((err_msg, 'HDD Root,')))
        log.error('%s is not a valid path' % hdd_root)

    # movie folder
    movie_folder = request.POST.get('MovieFolder', '')
    log.info('POST: movie_folder = %s' % movie_folder)
    if path.exists(movie_folder):
        movie_folder_db = MovieFolder.get_solo()
        movie_folder_db.relpath = movie_folder
        movie_folder_db.save()
        log.info('movie_folder = %s saved to db' % movie_folder)
    else:
        error = True
        err_msg = ' '.join((err_msg, 'Movie Folder,'))
        log.error('%s is not a valid path' % movie_folder)

    # tmdb key
    # TODO: check tmdb key is valid
    tmdb_key = request.POST.get('TMDB_KEY', '')
    log.info('POST: tmdb_key = %s' % tmdb_key)
    if len(tmdb_key) >= 5:
        tmdb_db = TMDbKey.get_solo()
        tmdb_db.key = tmdb_key
        tmdb_db.save()
        log.info('tmdb_key = %s saved to db' % tmdb_key)
    else:
        error = True
        err_msg = ' '.join(((err_msg, 'TMDb Key,')))
        log.error('%s is not a valid tmdb_key' % tmdb_key)

    # opensub
    # TODO: check opensub key is valid
    opensub_id = request.POST.get('OpenSubID', '')
    opensub_key = request.POST.get('OpenSubKey', '')
    log.info('opensub id:%s key:%s' % (opensub_id, opensub_key))
    if opensub_id and opensub_key:
        if len(opensub_id) >= 5 and len(opensub_key) >= 5:
            opensub_db = OpenSubKey.get_solo()
            opensub_db.uid = opensub_id
            opensub_db.key = opensub_key
            opensub_db.save()
            log.info('opensub id:%s key:%s saved to db' % (
                opensub_id, opensub_key
            ))
        else:
            error = True
            err_msg = ' '.join((err_msg, 'OpenSubtitles ID and Key,'))
            log.info('opensub id:%s key:%s are not valid' % (
                opensub_id, opensub_key
            ))

    if error is False:
        log.info('setup complete, redirected to welcome page')
        return render(
            request,
            'hdd_indexer/help.html',
            {
                'welcome': True,
            }
        )

    log.error('setup input has errors, redirect to setup page')
    return render(
        request,
        'hdd_indexer/setup.html',
        {
            'RegistrationKey': RegistrationKey,
            'hdd_name': hdd_name,
            'hdd_root': hdd_root,
            'movie_folder': movie_folder,
            'opensub_id': opensub_id,
            'opensub_key': opensub_key,
            'tmdb_key': tmdb_key,
            'error': error,
            'err_msg': err_msg,
        }
    )
