
* __auto-extract cleaned filenames from torrent files__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Fri, 7 Aug 2015 17:36:58 +0530
    
    Using regex, filenames are extracted and cleaned from torrent files. Correct,
    normal filenames are ignored and saved as is. Currently support two formats: 
    All movie filenames can contain alphanumeric characters and whitespace along
    with dash (-), underscore(_), and dot(.). Year can be within round () or square
    brackets [] 1. movie name followed by year in brackets 2. movie name followed
    by year in brackets followed by resolution(optional)
    
    closes #2 parse torrent filenames
    
    Signed-off-by: Harshvardhan Pandit &lt;coolharsh55@gmail.com&gt;
    

* __unified setup and start server with saved steps__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Fri, 7 Aug 2015 17:36:51 +0530
    
    The new command (python) hdd-indexer.py starts the setup if it has not been
    completed. It automatically starts the default web browser at localhost:8000 to
    complete the rest of the setup, or if it has been completed, start the
    homepage. The setup now stores its states in a file called .setup.py which is a
    pickled dictionary.
    
    Closes #7 save setup status and steps
    
    Signed-off-by: Harshvardhan Pandit &lt;coolharsh55@gmail.com&gt;
    

* __Admin interfaces for Actor and Director__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Fri, 7 Aug 2015 17:36:10 +0530
    
    Admin interfaces for Actors and Directors that shows how many movies an actor
    has acted in, if they are a director, and how many movies they have directed.
    Also shows the same info for directors. Abstract Person models allow changing
    the basic info about a person such as name.
    
    Closes #19 Admin for Actor Closes #20 Admin for Director
    
    Signed-off-by: Harshvardhan Pandit &lt;coolharsh55@gmail.com&gt;
    

* __fixes #17 opensub CannotSendRequest error__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Fri, 7 Aug 2015 16:55:35 +0530
    
    Used a function.dict stored lock to allow only one thread to connect to OpenSub
    at a time. Also moved the token code to the function init code where sub is
    instantiated. This allows the entire load operation to be completed with just
    one token instead of individual token for every request.
    
    Signed-off-by: Harshvardhan Pandit &lt;coolharsh55@gmail.com&gt;
    

* __fixes #18 movie.py logging person error__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Fri, 7 Aug 2015 16:53:47 +0530
    
    The logging statement was erroenous as it tried to print variables without a
    matching position. log(&#39;$s&#39; % s) instead of log(&#39;%s&#39; %s)
    
    Signed-off-by: Harshvardhan Pandit &lt;coolharsh55@gmail.com&gt;
    

* __install dependency python-opensubtitles  via pip__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Thu, 6 Aug 2015 16:11:22 +0530
    
    python-opensubtitles can now be installed via pip (using -e) option
    
    resolves #1 resolves #16
    
    Signed-off-by: Harshvardhan Pandit &lt;coolharsh55@gmail.com&gt;
    

* __add waffle.io badge__

    [Making GitHub Delicious.](iron@waffle.io) - Mon, 3 Aug 2015 12:41:31 -0600
    
    

* __new: logging (level=debug) in all used modules and views__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Mon, 3 Aug 2015 21:19:44 +0530
    
    system: logs/system.log server requests: logs/server.log load: logs/load.log 
    crawl: logs/crawl.log movie save: logs/movie.log
    
    new: uses the tmdbsimple library
    
    tmdbsimple is used for searching on tmdb by title as default, and by imdb only
    when omdb fails
    
    fix: race condition when updating counters which sometimes caused the counter
    to display incorrect values
    
    The loader status counters sometimes get updated to the same value in two
    different threads. Fixed by using a threading lock before write.
    
    chg: opensub initialization is now done only once
    
    OpenSub was initialised in every thread before. Now it uses only one authorised
    object to perform searches. This results in performance and time benefits.
    
    chg: skipped list moved to loader status
    
    The skipped list has been moved into the loader status, and is accessed by all
    threads directly. The locks prevent race conditions and ensure that each list
    update is correctly reflected.
    
    removed: tmdb cast and crew
    
    tmdb simple does not support (as far as I know) retrieving cast and crew
    directly.
    

* __new: logging config for system, server, load, crawl, movie, and setup__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Mon, 3 Aug 2015 20:52:52 +0530
    
    All logs are stored in /logs
    

* __chg: remove tmdb3==0.7.2 library__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Mon, 3 Aug 2015 09:00:23 +0530
    
    tmdb3 library (pytmdb3) had buffer read errors that resulted in errors during
    movie search by title
    

* __new: coveralls integration__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Wed, 29 Jul 2015 19:56:52 +0530
    
    

* __new: travis-ci build configuration__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Wed, 29 Jul 2015 19:12:48 +0530
    
    

* __chg: install tmdb3 via pip, opensubtitles via git clone__

    [Harshvardhan Pandit](coolharsh55@gmail.com) - Wed, 29 Jul 2015 18:40:00 +0530
    
    
    

