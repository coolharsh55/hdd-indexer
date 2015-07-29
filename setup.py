"""Setup for HDD-indexer

This module provides the setup for ``hdd-indexer`` by downloading its
`dependencies`, creating the `database`, createing a sampel `user`, and
starting the `webserver` and browser at ``localhost:8000``

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
import subprocess
import time
import urllib2
import webbrowser


def start():
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

    # Welcome message
    cls()
    print 'Welcome to HDD-indexer'
    print '----------------------'
    print '----------------------'
    print "Let's start with the setup."

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
    print "Excellent! We're set!"
    raw_input("Press Enter to continue...")

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
    raw_input("Press Enter to continue...")

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
    print 'Alright, done!'
    raw_input("Press Enter to continue...")

    # Webserver + Browser
    cls()
    print "Now comes the nice part...!"
    print "Let's start HDD-indexer!"
    print "HDD-indexer is browser based."
    print "So, you can always find it at localhost:8000"
    print "I'm going to start the server here, in this window."
    print "And I'll also open the webpage in a browser for you, OK?"
    # Terminate AFTER starting the server using CTRL + C
    print "(hint: To terminate the server, just press CTRL+C here.)"
    raw_input("Press Enter to continue...")
    # python manage.py runserver
    cmd = ['python', 'manage.py', 'runserver']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    time.sleep(3)
    # default ip 192.168.0.1
    # default port 8000
    # TODO: param to open webserver at another address:port
    webbrowser.open('http://localhost:8000/setup')
    for line in p.stdout:
        print line,
    p.wait()
    if p.returncode:
        print 'ERROR! ERROR! ERROR!'
        print "Let's hope it goes away :("
        return

    print "Good-bye!"
    return


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
    start()
