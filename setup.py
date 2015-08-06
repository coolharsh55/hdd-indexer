"""Setup for HDD-indexer

This module provides the setup for ``hdd-indexer`` by downloading its
`dependencies`, creating the `database`, createing a sampel `user`.

Usage:
        $ python setup.py

Dependencies:
    The dependencies are installed with pip.
        $ pip install -r requirements.txt

Database:
    The database is created via `migrations` from `django`
        $ python manage.py migrate

Superuser:
    The superuser is created for accessing the admin interface.
    It has the crendentials `u:user` and `p:pass`
        $ python manage.py createsuperuser
        username: user
        email: user@example.com
        password: pass

Webserver:
    The django webserver is started at localhost port 8000
        $ python manage.py runserver

Browser:
    A browser page is opened at localhost:8000 to continue setup.
"""

import os
import platform
import pickle
import subprocess
import urllib2


PICKLED_SETUPFILE = './.setup.pickle'
SETUP_STATUS = {}


def depickle_setup():
    """Load setup status from pickle

    Args:
        None

    Returns:
        dict:
            console_completed(bool): console setup completed
            last_complete(bool): whether the last setup completed
                successfully
            installed_dependencies(bool): installed dependencies
            database_migrate(bool): database migrated
            user_admin(bool): create an admin user

    Raises:
        None
    """

    try:
        if os.path.isfile(PICKLED_SETUPFILE):
            # setup pickle exists, has been written previously
            with open(PICKLED_SETUPFILE, 'r') as file:
                setup_status = pickle.load(file)
                # TODO: assert setup status is a dict
                # TODO: assert setup status fields are present
                # TODO: assert setup status values are valid
                return setup_status
        else:
            # setup pickle does not exist, setup run first time
            setup_status = {
                'console_completed': False,
                'last_completed': False,
                'installed_dependencies': False,
                'database_migrate': False,
                'user_admin': False,
            }
            pickle_setup(setup_status)
            return setup_status
    except Exception:
        pass
        # TODO: logging


def pickle_setup(setup_dict):
    """Save setup status to pickle

    Args:
        setup_dict(dict):
            console_completed(bool): console_setup_completed
            last_complete(bool): whether the last setup completed
                successfully
            installed_dependencies(bool): installed dependencies
            database_migrate(bool): database migrated
            user_admin(bool): create an admin user

    Returns:
        None

    Raises:
        None
    """
    assert type(setup_dict) == dict
    # TODO: check setup dict has valid keys
    # TODO: check setup dict has valid values
    try:
        with open(PICKLED_SETUPFILE, 'w') as file:
            pickle.dump(setup_dict, file)
    except Exception:
        pass
        # TODO: logging


def welcome_message():
    """
    """
    # Welcome message
    cls()
    print 'Welcome to HDD-indexer'
    print '----------------------'
    print '----------------------'
    if SETUP_STATUS['last_completed']:
        print "Let's start with the setup."
    else:
        print "Let's continue with the setup."


def install_dependencies():
    # Internet checkup
    print "We'll make sure you are connected to the internet first."
    raw_input("Press Enter to continue...")
    if not internet_on():
        print 'What! No Internet...? :('
        return  # cannot install dependencies without the internet
    print 'Oooh... Connectivity! :)'
    raw_input("Press Enter to continue...")

    # Dependencies
    cls()
    print "The first thing we'll do is install the dependencies"
    raw_input("Press Enter to continue...")
    # pip install -r requirements.txt
    # TODO: assert requirements.txt exists
    cmd = ['pip', 'install', '-r', 'requirements.txt']
    # open a subprocess and pipe its output
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in p.stdout:
        print line,
    p.wait()
    if p.returncode:
        print 'ERROR! ERROR! ERROR!'
        return
    SETUP_STATUS['installed_dependencies'] = True
    pickle_setup(SETUP_STATUS)
    print "Excellent! We're set!"
    raw_input("Press Enter to continue...")


def database_migrate():
    """
    """
    # Database
    cls()
    print "Now let's setup the database for you..."
    raw_input("Press Enter to continue...")
    print '----------------------'
    print 'MIGRATING DATABASE'
    # python manage.py migrate
    # This will run django's migrations, which creates the database
    #   and its associated tables / schema
    cmd = ['python', 'manage.py', 'migrate']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    for line in p.stdout:
        print line,
    p.wait()
    if p.returncode:
        print 'ERROR! ERROR! ERROR!'
        return
    SETUP_STATUS['database_migrate'] = True
    pickle_setup(SETUP_STATUS)
    raw_input("Press Enter to continue...")


def create_user_admin():
    """
    """
    # User
    cls()
    print "Now that it's done, let's create a user for you!"
    print '----------------------'
    print "username: user"
    print "password: pass"
    print '----------------------'
    print "You ready?"
    raw_input("Press Enter to continue...")
    # load django's settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hdd_indexer.settings")
    import django  # import django inline only when required
    django.setup()  # call django to load its settings
    from django.contrib.auth.models import User
    try:
        # get the user with u=user
        p = User.objects.get(username='user')
        # if exists, delete it
        p.delete()
    except User.DoesNotExist:
        # does not exist, therefore let's it
        # TODO: check if pass can be changed programmatically instead of
        #   deleting the user and creating it again
        pass
    User.objects.create_superuser('user', 'user@example.com', 'pass')
    SETUP_STATUS['user_admin'] = True
    pickle_setup(SETUP_STATUS)
    print 'Alright, done!'
    raw_input("Press Enter to continue...")


def start(setup_status):
    """Start - starts the setup

    start carries the main function calls for setup.py.
    It notifies the user about each step, and waits for conformation.
    No notice or cancellation is allowed explicitly.
    If the user wishes to quit, they can do so by breaking the setup.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """

    global SETUP_STATUS
    SETUP_STATUS = setup_status
    welcome_message()

    err = None

    if not SETUP_STATUS['installed_dependencies'] and not err:
        err = install_dependencies()

    if not SETUP_STATUS['database_migrate'] and not err:
        err = database_migrate()

    if not SETUP_STATUS['user_admin'] and not err:
        err = create_user_admin()

    if not err:
        SETUP_STATUS['console_completed'] = True
    else:
        SETUP_STATUS['console_completed'] = False
    pickle_setup(SETUP_STATUS)
    return SETUP_STATUS


def internet_on():
    """Check if internet connectivity is present

    The function checks if internet is on by connecting to a
    website (www.google.co.in) and analysing its response.

    Args:
        None

    Returns:
        bool: True if ON, False otherwise.

    Raises:
        None
    """
    try:
        urllib2.urlopen('http://216.58.196.99', timeout=10)
        return True
    except urllib2.URLError:
        pass
    return False


def cls():
    """Clear Screen

    The function clears the screen in any platform (POSIX / Windows).
    It checks which system is running and uses the approporiate commands
    based on the default terminal.

    For Windows:
        platform.system returns 'Windows'
        screen can be cleared in terminal using 'clear'
    For Others:
        screen can be cleared using 'cls' across all POSIX systems

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    if platform.system() != 'Windows':
        subprocess.call("clear")  # linux/mac
    else:
        subprocess.call("cls", shell=True)  # windows


if __name__ == '__main__':
    print 'Please use (python) hdd-indexer.py'
