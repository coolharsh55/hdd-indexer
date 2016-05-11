"""Exporter

    Exports movies saved in database

    File Formats:
        txt, csv

    Filtering options:
        director, release date, rating

    Ordering options:
        alphabetical, date/time, rating
"""

import cStringIO as StringIO
import logging
import json
import traceback
log = logging.getLogger('export')
log.info(72 * '-')
log.info('exporter loaded')

_FILE_FORMATS = {
    'txt': '\t',
    'csv': ',',
    'json': '',
}

log.info('supported file formats: %s' % _FILE_FORMATS.keys())

# TODO: dict for file formats and then supply them with names
# such as separator, filename = _FF[file_format] should get
# \t and movie_list.txt
#
# TODO: exporter GUI
# show in modal all the options as checkboxes
# GET request for getting exporter file
# show swal where necessary
# parse checkbox to create field and ordering list
# get file, and serve it
# show swal for download complete or error


def export(
        model,
        file_format='txt',
        fields=[],
        filter=[],
        order=[],):
    """export movies to file
    """
    try:
        assert type(model).__name__ == 'ModelBase'
        assert type(file_format) == str or type(file_format) == unicode
        assert file_format in _FILE_FORMATS.keys()
        assert hasattr(fields, '__iter__') and len(fields) > 0
        assert hasattr(filter, '__iter__')
        assert hasattr(order, '__iter__')
    except AssertionError:
        log.error(traceback.format_exc())
        return None

    log.info('request %s.%s with fields=%s, filter=%s, ordering=%s' % (
        model.__name__, file_format, fields, filter, order))
    # file is an in-memory string buffer
    export_file = StringIO.StringIO()
    # get all objects from database using filter and query
    objects = model.objects.filter(*filter).order_by(*order)
    # get fields in Model
    model_fields = [field.name for field in model._meta.fields]
    # choose only available attributes
    attributes = []
    for field in fields:
        if field in model_fields:
            attributes.append(field)
        else:
            print 'incorrect field: %s' % field

    # populate file with objects
    if file_format == 'json':
        movies = {}
        for obj in objects:
            if obj.imdb_id:
                movies[obj._id] = {
                    'imdb_id': obj.imdb_id,
                    'title': obj.title,
                    'release_date': str(obj.release), }
            else:
                pass

        dump = json.dumps(
            movies, sort_keys=True, indent=4, separators=(',', ': '))
        export_file.write(dump)
        return export_file.getvalue()

    separator = _FILE_FORMATS[file_format]
    for obj in objects:
        val = []
        # get each attribute from object
        for attribute in attributes:
            value = getattr(obj, attribute)
            if value:
                if type(value) == unicode or type(value) == str:
                    # encode unicode
                    value = value.encode('utf-8')
                else:
                    value = str(value)
            else:
                # null values are N/A
                value = 'N/A'
            val.append(value)
        # tabs as column separators
        content = separator.join(val)
        export_file.write(content)
        # newline row separators
        export_file.write('\n')

    # return content stream
    return export_file.getvalue()
