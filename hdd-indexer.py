"""HDD-Indexer

HDD-indexer is an utility that looks for movie files on a
disk and cataloges them along with their metadata. It uses
various online services to retrieve movie metadata such as
release date, ratings, cast, and crew.

If this is the first time the program is run, it wil start
the setup. The setup is two-part, with the first one in
the console, and the second one run in the browser.

It will automatically open your default browser and
start the `webserver` and browser at ``localhost:8000``

Usage:
        $ python hdd-indexer.py


"""

import time
import setup
import subprocess
import webbrowser

if __name__ == '__main__':
    setup_status = setup.depickle_setup()
    if setup_status['console_completed'] is not True:
        setup_status = setup.start(setup_status)
        print "Now comes the nice part...!"

    setup.cls()
    print "Let's start HDD-indexer!"
    print ""
    print "HDD-indexer is browser based."
    print "So, you can always find it at"
    print ""
    print ""
    print "    >>>  localhost:8000  <<<"
    print ""
    print ""
    print "I'm going to start the server here, in this window."
    print "And I'll also open the webpage in a browser for you, OK?"
    print ""
    # Terminate AFTER starting the server using CTRL + C
    print "(hint: To terminate the server, just press CTRL+C here.)"
    print "(tip: To reset HDD-indexer, delete db.sqlite3 and .setup.pickle)"
    print ""
    raw_input("Press Enter to continue...")
    # python manage.py runserver
    cmd = ['python', 'manage.py', 'runserver']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    time.sleep(3)
    # default ip 192.168.0.1
    # default port 8000
    # TODO: param to open webserver at another address:port
    if setup_status['last_completed'] is not True:
        webbrowser.open('http://localhost:8000/setup')
        setup_status['last_completed'] = True
        setup.pickle_setup(setup_status)
    else:
        webbrowser.open('http://localhost:8000/')
    for line in p.stdout:
        print line,
    p.wait()
    if p.returncode:
        print 'ERROR! ERROR! ERROR!'
        print "Let's hope it goes away :("

    print "Good-bye!"
