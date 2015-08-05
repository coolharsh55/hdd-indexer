"""Crawl hdd looking for movie files

    The crawl module browses the movie_folder specified in the
    database looking for movie files. It uses a tuple containing
    the movie extensions and checks for movies based on a threshold
    file size.

    Usage:
        $ from movie_metadata import crawl
        $ crawl.function_name()
"""

from os import path
from os import stat
from os import walk
import threading
import logging
log = logging.getLogger('crawl')
log.info(72*'-')
log.info('crawl module loaded')

from hdd_settings.models import HDDRoot
from hdd_settings.models import MovieFolder
from movie_metadata.models import Movie

# TODO: video filetypes as model
# TODO: movie size threshold as solo object
_VIDEO_FILETYPES = (
    '.264', '.3g2', '.3gp', '.3gp2', '.3gpp', '.3gpp2', '.3mm', '.3p2', '.60d',
    '.787', '.89', '.aaf', '.aec', '.aep', '.aepx',
    '.aet', '.aetx', '.ajp', '.ale', '.am', '.amc', '.amv', '.amx', '.anim',
    '.aqt', '.arcut', '.arf', '.asf', '.asx', '.avb', '.avc', '.avd', '.avi',
    '.avp', '.avs', '.avs', '.avv', '.axm', '.bdm', '.bdmv', '.bdt2', '.bdt3',
    '.bik', '.bin', '.bix', '.bmk', '.bnp', '.box', '.bs4', '.bsf', '.bvr',
    '.byu', '.camproj', '.camrec', '.camv', '.ced', '.cel', '.cine', '.cip',
    '.clpi', '.cmmp', '.cmmtpl', '.cmproj', '.cmrec', '.cpi', '.cst', '.cvc',
    '.cx3', '.d2v', '.d3v', '.dat', '.dav', '.dce', '.dck', '.dcr', '.dcr',
    '.ddat', '.dif', '.dir', '.divx', '.dlx', '.dmb', '.dmsd', '.dmsd3d',
    '.dmsm', '.dmsm3d', '.dmss', '.dmx', '.dnc', '.dpa', '.dpg', '.dream',
    '.dsy', '.dv', '.dv-avi', '.dv4', '.dvdmedia', '.dvr', '.dvr-ms', '.dvx',
    '.dxr', '.dzm', '.dzp', '.dzt', '.edl', '.evo', '.eye', '.ezt', '.f4p',
    '.f4v', '.fbr', '.fbr', '.fbz', '.fcp', '.fcproject', '.ffd', '.flc',
    '.flh', '.fli', '.flv', '.flx', '.gfp', '.gl', '.gom', '.grasp', '.gts',
    '.gvi', '.gvp', '.h264', '.hdmov', '.hkm', '.ifo', '.imovieproj',
    '.imovieproject', '.ircp', '.irf', '.ism', '.ismc', '.ismv', '.iva',
    '.ivf', '.ivr', '.ivs', '.izz', '.izzy', '.jss', '.jts', '.jtv', '.k3g',
    '.kmv',
    '.ktn', '.lrec', '.lsf', '.lsx', '.m15', '.m1pg', '.m1v', '.m21', '.m21',
    '.m2a', '.m2p', '.m2t', '.m2ts', '.m2v', '.m4e', '.m4u', '.m4v', '.m75',
    '.mani', '.meta', '.mgv', '.mj2', '.mjp', '.mjpg', '.mk3d', '.mkv', '.mmv',
    '.mnv', '.mob', '.mod', '.modd', '.moff', '.moi', '.moov', '.mov',
    '.movie',
    '.mp21', '.mp21', '.mp2v', '.mp4', '.mp4v', '.mpe', '.mpeg', '.mpeg1',
    '.mpeg4', '.mpf', '.mpg', '.mpg2', '.mpgindex', '.mpl', '.mpl', '.mpls',
    '.mpsub', '.mpv', '.mpv2', '.mqv', '.msdvd', '.mse', '.msh', '.mswmm',
    '.mts', '.mtv', '.mvb', '.mvc', '.mvd', '.mve', '.mvex', '.mvp', '.mvp',
    '.mvy', '.mxf', '.mxv', '.mys', '.ncor', '.nsv', '.nut', '.nuv', '.nvc',
    '.ogm', '.ogv', '.ogx', '.osp', '.otrkey', '.pac', '.par', '.pds', '.pgi',
    '.photoshow', '.piv', '.pjs', '.playlist', '.plproj', '.pmf', '.pmv',
    '.pns',
    '.ppj', '.prel', '.pro', '.prproj', '.prtl', '.psb', '.psh', '.pssd',
    '.pva',
    '.pvr', '.pxv', '.qt', '.qtch', '.qtindex', '.qtl', '.qtm', '.qtz', '.r3d',
    '.rcd', '.rcproject', '.rdb', '.rec', '.rm', '.rmd', '.rmd', '.rmp',
    '.rms',
    '.rmv', '.rmvb', '.roq', '.rp', '.rsx', '.rts', '.rts', '.rum', '.rv',
    '.rvid', '.rvl', '.sbk', '.sbt', '.scc', '.scm', '.scm', '.scn',
    '.screenflow', '.sec', '.sedprj', '.seq', '.sfd', '.sfvidcap', '.siv',
    '.smi', '.smi', '.smil', '.smk', '.sml', '.smv', '.spl', '.sqz', '.srt',
    '.ssf', '.ssm', '.stl', '.str', '.stx', '.svi', '.swf', '.swi', '.swt',
    '.tda3mt', '.tdx', '.thp', '.tivo', '.tix', '.tod', '.tp', '.tp0', '.tpd',
    '.tpr', '.trp', '.ts', '.tsp', '.ttxt', '.tvs', '.usf', '.usm', '.vc1',
    '.vcpf', '.vcr', '.vcv', '.vdo', '.vdr', '.vdx', '.veg', '.vem', '.vep',
    '.vf', '.vft', '.vfw', '.vfz', '.vgz', '.vid', '.video', '.viewlet',
    '.viv',
    '.vivo', '.vlab', '.vob', '.vp3', '.vp6', '.vp7', '.vpj', '.vro', '.vs4',
    '.vse', '.vsp', '.w32', '.wcp', '.webm', '.wlmp', '.wm', '.wmd', '.wmmp',
    '.wmv', '.wmx', '.wot', '.wp3', '.wpl', '.wtv', '.wve', '.wvx', '.xej',
    '.xel', '.xesc', '.xfl', '.xlmv', '.xmv', '.xvid', '.y4m', '.yog', '.yuv',
    '.zeg', '.zm1', '.zm2', '.zm3', '.zmv', )
"""Video File Extensions
    File extensions for identifying movie files
"""
log.info('videos extensions')
log.info(_VIDEO_FILETYPES)

_MOVIE_SIZE_THRESHOLD = 300000000  # 300MB
"""File size threshold to differentiate videos and movies
"""
log.info('movie size threshold: %s' % _MOVIE_SIZE_THRESHOLD)

_ERROR = {
    1: 'HDD Root not configured properly.',
    2: 'Movie Folder not configured properly.',
}
"""Crawler Error messages
"""


def crawler_status(key=None, value=None):
    """Crawler status

    Args:
        key(dict key): key to search in dict
        value(dict value): value to assign to key

    Returns:
        bool: True for ON, False for OFF
    """
    if 'status' not in crawler_status.__dict__:
        crawler_status.status = {
            'STATUS': False,
            'FILES_EVALUATED': 0,
            'MOVIES_FOUND': 0,
            'MOVIES_ADDED': 0,
        }
    _CRAWLER = crawler_status.status
    if _CRAWLER.get(key) is not None:
        if value is not None:
            log.info('crawler status: %s -> %s' % (key, value))
            _CRAWLER[key] = value
        else:
            return _CRAWLER[key]
    return _CRAWLER['STATUS']


def start_crawler():
    """Start the crawler

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    log.info('start crawler')
    hdd_root = HDDRoot.get_solo().path
    if not path.exists(hdd_root):
        print _ERROR[1]
        log.error('%s is not a valid hdd root path' % hdd_root)
        return _ERROR[1]
    movie_folder = MovieFolder.get_solo().relpath
    if not path.exists(path.join(hdd_root, movie_folder)):
        print _ERROR[1]
        log.error('%s is not a valid movie folder path' % movie_folder)
        return _ERROR[2]
    crawler_status('STATUS', True)
    crawler_status('FILES_EVALUATED', 0)
    crawler_status('MOVIES_FOUND', 0)
    crawler_status('MOVIES_ADDED', 0)
    thread = threading.Thread(target=crawl_movies)
    thread.daemon = True
    thread.start()
    log.info('crawl started on daemon thread')


def stop_crawler():
    """Stop the crawler

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    log.info('crawler stopped')
    crawler_status('STATUS', False)


def crawl_movies():
    """Crawl for Movies on HDD

    Looks for movies on the HDD based on file extensions and
    threshold size. Saves them to database.

    Args:
        None

    Returns:
        None

    Raises:
        AssertionError
    """
    movie_folder_path = path.join(
        HDDRoot.get_solo().path,
        MovieFolder.get_solo().relpath,
    )
    log.info('crawl movie folder path : %s' % movie_folder_path)
    files_evaluated = 0
    movies_found = 0
    movies_added = 0
    for root, dirs, files in walk(movie_folder_path):
        for filename in files:
            files_evaluated += 1
            crawler_status('FILES_EVALUATED', files_evaluated)
            if not crawler_status():
                return
            name, ext = path.splitext(filename)
            if ext not in _VIDEO_FILETYPES:
                continue

            filepath = path.join(root, filename)
            size = stat(filepath).st_size
            if size < _MOVIE_SIZE_THRESHOLD:
                continue

            movies_found += 1
            crawler_status('MOVIES_FOUND', movies_found)
            relpath = path.relpath(
                filepath,
                path.join(
                    HDDRoot.get_solo().path,
                    MovieFolder.get_solo().relpath,
                ),
            )
            log.debug('movie found at %s' % relpath)

            if _movie_exists_with_relpath(relpath):
                log.debug('%s exists in db' % relpath)
                continue

            movie = Movie()
            movie.title = name
            movie.relpath = relpath
            movie.save()
            movies_added += 1
            log.info('%s added to database' % movie.title)
            crawler_status('MOVIES_ADDED', movies_added)
    crawler_status('STATUS', False)


def _movie_exists_with_relpath(relpath):
    """Check Movie exists in database by its relative path

    Args:
        relpath(str): relative path of file from Movie Folder

    Returns:
        bool: True if found, False otherwise
    """

    assert type(relpath) == str or type(relpath) == unicode
    assert path.isfile(
        path.join(
            HDDRoot.get_solo().path,
            MovieFolder.get_solo().relpath,
            relpath,
        )
    )

    count = Movie.objects.filter(relpath=relpath).count()

    if count > 1:
        print 'Found movie, and duplicates (relpath) exist.'
        log.warning('%s duplicates exist in database' % relpath)
        return True

    if count == 1:
        return True

    return False
