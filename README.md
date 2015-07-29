# HDD-indexer
[![Build Status](https://travis-ci.org/coolharsh55/hdd-indexer.svg)](https://travis-ci.org/coolharsh55/hdd-indexer)

**hdd-indexer** is an utility that indexes the contents of a hard disk, and allows viewing and interacting with it based on **metadata**. Currently, it supports only *video* files, specifically *movies*.

## Features:

### Available:
 - Identify movies on disk and save them in a database
 - Download metadata such as release date, cast, crew, and ratings from online sources
 - Filter and sort movies using metadata

### Planned:
- Organise movies on disk automatically by their metadata such as release year, director, genre, etc.
- Compare contents of two disks to create a share/lend/borrow list
- Remote storage of disk index so that it can be viewed by others
- Export list of movies. Sort and filter based on metadata.

## Use:

### Requirements / Dependencies:

##### Pre-requisites:
The project requires **python2.7** to be installed. It has not been tested on *python3*.

##### Dependencies:
###### Available via pip
- Django==1.8.2
- django-grappelli==2.6.5
- django-solo==1.1.0
- tmdb3==0.7.2

###### Manually download python-opensubtitles
Download the library from [python-opensubtitles](https://github.com/agonzalezro/python-opensubtitles) and movie the **pythonopensubtitles** folder to the project directory,

*OR*

using git: 

```git clone --depth=1 git://github.com/agonzalezro/python-opensubtitles && mv python-opensubtitles/pythonopensubtitles ./ && rm -rf python-opensubtitles```

### Installing
1. Download the project
2. Make sure you have downloaded the *python-opensubtitles* into the project directory.
3. Start the setup using ```python setup.py```
4. It will **fail** if there is *no internet connectivity*.
5. It will install dependencies via *pip*
6. It will create the *database* and associated *tables/schema* using django's *manage.py migrate*
7. It creates an admin user
8. Next, it will start the server, and open a browser page to **localhost:8000** to complete the rest of the setup.
9. In the browser, enter the fields specified.
10. The **registration key** can be any non-empty string *for now*
11. The **HDD Name** is a semantic name for the disk
12. The **HDD Root** is the mount path of the disk on the current system. For _*NIX_ systems, enter the path from root to the mount directory (*/root/to/mount/*). For Windows, enter the drive letter along with a colon (*E:*)
13. The **Movie Folder** is the path to the folder containing all the movie files. The path should be a valid and existing path, which can be verified using *python's* ```os.path.exists(...)``` Spaces in the path are automatically resolved. 
14. Enter the keys for using APIs of *OpenSubtitles* and *TMDb*. Links to registration are provided on the setup page.
15. Finally, upon successful setup completion, the **help page** will open showing a **Quick Start** quide.

### Starting the server and interface
1. start the server using ```python migrate.py runserver``` . This is a *django* command that starts a local server at **localhost** and port **8000**, both of which can be changed by passing parameters to the command.
2. Open a browser at **localhost:8000**

### Modules
#### Browse
Browse movies, cast, and crew present in database using *django's admin interface*. Movies can be viewed as *lists*, that can be filtered or sorted based on metadata such as title, release date, cast, crew, ratings, etc.

#### Crawl
Crawls the hard disk looking for movies and adds them to database. The crawler is usually fast to operate since it only looks at file extensions and file size to identify movies.

#### Load
Downloads and updates metadata for movies in database. The loader requires internet connectivity and will not function without it. It can take a substantial amount of time based on number of movies in database. Since this is not a complete release, some times the loader module can get stuck. You can stop the module safely in such cases.

## More Info

### Framework - Django/py2.7
This is a **django** project that uses the local server functionality to serve a movie database. Since both server and client are on the same machine, the interface is fluid and  responsive. Using django also allows for all data/info/settings to be stored in database.

### Database - SQLite3
The database is stored as a local database file named **db.sqlite3** in the hdd_indexer folder. To backup or copy the databae, use this file.

## Bugs and Issues
Currently, this build is in early stages and there are bound to be several bugs and issues. Please help its development by filing these in the bug/issue tracker, or email me.

## Blog and Contact
The project blog is at [hdd-indexer at harshp.com](http://brainbank.harshp.com/hdd-indexer/)

You can contact me regarding ideas, issues, bugs, and collaborations at **hdd-indexer@harshp.com**