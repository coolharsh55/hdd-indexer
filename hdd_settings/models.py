"""Models for settings
"""

# TODO: docstrings
# TODO: test 'undefined' values are not accepted

from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible
from django.db import models
from solo.models import SingletonModel
import os
import re


@python_2_unicode_compatible
class RegistrationKey(SingletonModel):
    key = models.CharField(
        max_length=20,
        default='undefined',
        verbose_name='Registration Key',
        help_text='''Key used to register the HDD on remote server'''
    )

    def __str__(self):
        """String representation of RegistrationKey

        Args:
            None

        Returns:
            key(str): registration key

        Raises:
            None

        """
        return self.key


@python_2_unicode_compatible
class HDDName(SingletonModel):
    """HDD Name

    A semantic name for the disk used to identify it when comparing against
    another remote or local disk.

    Attributes:
        name(str): name of the hdd, defaults to 'undefined'
    """
    name = models.CharField(
        max_length=500,
        default='undefined',
        verbose_name='HDD Name',
        help_text='''The semantic name used to identify the disk''',)

    def __str__(self):
        """String representation of HDDName

        Args:
            self: current instance of HDDName

        Returns:
            name(str): name of hdd

        Raises:
            None
        """
        return self.name

    def save(self, *args, **kwargs):
        """Save HDDName to database

        checks if the name is valid using regex pattern
        only digits, letters, and `_(underscore), -(dash)` are allowed.

        Args:
            self: current instance of HDDName
            *args: arguments passed by system
            **kwargs: keyword arguments passed by system

        Returns:
            calls super()

        Raises:
            ValueError: invalid HDD name
        """
        pattern = re.compile(r'^[0-9a-zA-z_-]+$')
        if not pattern.match(self.name):
            raise ValueError('Error! HDD Name is invalid')
        return super(HDDName, self).save(*args, **kwargs)


@python_2_unicode_compatible
class HDDRoot(SingletonModel):
    """HDD Root

    Root path of the hdd on current system. This will change (on system)
    based on how the drive is mounted on this or other systems.
    The HDD root is the folder containing the disk contents.
    For example-
            disk is mounted in /Volumes/disk-name
            Then the root path is /Volumes/disk-name

            disk is mounted in X:
            Then the root path is X:

    Attributes:
        path(str): absolute path of the hdd root, defaults to '/'
    """
    path = models.CharField(
        max_length=500,
        verbose_name='HDD root path',
        default='/',
        help_text='''The path of the disk on the current system''')

    def __str__(self):
        """String representation of HDD root

        Args:
            self: current instance of HDD root

        Returns:
            path(str): hdd root path

        Raises:
            None
        """
        return self.path

    def save(self, *args, **kwargs):
        """Save HDDRoot to database

        check if path is a valid directory

        Args:
            self: current instance of HDDRoot
            *args: arguments passed by system
            **kwargs: keyword arguments passed by system

        Returns:
            calls super()

        Raises:
            ValueError: invalid path
        """
        ''' before saving, check path is folder '''
        if not os.path.isdir(self.path):
            raise ValueError('The specified path is a not a valid.')
        return super(HDDRoot, self).save(*args, **kwargs)


@python_2_unicode_compatible
class MovieFolder(SingletonModel):
    """Movie Folder

    The folder containing the movies on hdd.

    Attributes:
        relpath(str): relative path of the folder from hdd-root
    """
    # TODO: Multiple Movie Folders on the hard disk
    relpath = models.CharField(
        max_length=500,
        verbose_name='Movie folder path',
        default='/',
        help_text='''
            The path for the Movie folder
            relative to the HDD root''',)
    slug = models.SlugField(max_length=500,)

    def __str__(self):
        """String representation of MovieFolder

        Args:
            self: current instance of MovieFolder

        Returns:
            relpath(str): relative path of movie folder from hdd root

        Raises:
            None
        """
        return self.relpath

    def save(self, *args, **kwargs):
        """Save MovieFolder to database

        checks if movie folder path is a valid path by appending it
        to the hdd-root path to get the absolute path of movie folder

        Args:
            self: current instance of MovieFolder
            *args: arguments passed by system
            **kwargs: keyword arguments passed by system

        Returns:
            calls super()

        Raises:
            ValueError: invalid movie folder path
        """
        hdd_root = HDDRoot.get_solo()
        if not os.path.isdir(os.path.join(hdd_root.path, self.relpath)):
            raise ValueError('The specified path is a not a valid folder.')
        return super(MovieFolder, self).save(*args, **kwargs)


@python_2_unicode_compatible
class TMDbKey(SingletonModel):
    """
    """
    key = models.CharField(
        max_length=25,
        default='undefined',
        verbose_name='TMDb API Key',
        help_text='Key used to acquire token from TMDb API',
    )

    def __str__(self):
        """String representation of TMDbKey

        Args:
            None

        Returns:
            key(str): api key

        Raises:
            None
        """
        return self.key


@python_2_unicode_compatible
class OpenSubKey(SingletonModel):
    """
    """
    uid = models.CharField(
        max_length=25,
        default='undefined',
        verbose_name='OpenSubtitles API ID',
        help_text='ID used to acquire token from OpenSubtitles API',
    )
    key = models.CharField(
        max_length=25,
        default='undefined',
        verbose_name='OpenSubtitles API Key',
        help_text='Key used to acquire token from OpenSubtitles API',
    )

    def __str__(self):
        """String representation of OpenSubtitles API

        Args:
            None

        Returns:
            key(str): api key

        Raises:
            None
        """
        return ''.join((self.id, '--', self.key))
