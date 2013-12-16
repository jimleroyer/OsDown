#!/usr/bin/env python
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
import ConfigParser
import urllib
from tempfile import mktemp
import gzip
from numbers import Number
import os
from os import path


config = ConfigParser.RawConfigParser()
config.read(os.path.realpath(__file__)[:-2] + 'cfg')
osmgr = OpenSubtitles()
osmgr.login(config.get('Login', 'user'), config.get('Login', 'pass'))


def find_subtitles(path, langid='all'):
    ''' Get a list of subtitles for a given file '''
    f = File(path)
    hash = f.get_hash()
    assert type(hash) == str
    size = f.size
    assert isinstance(size, Number)
    data = osmgr.search_subtitles([{'sublanguageid': langid,
                                   'moviehash': hash,
                                   'moviebytesize': size}])
    assert type(data) == list
    return data


def download_subtitle(subtitle):
    print 'Downloading %s...' % subtitle['SubFileName']
    tempfile = mktemp()
    urllib.urlretrieve(subtitle['SubDownloadLink'], tempfile)
    with gzip.open(tempfile, 'rb') as gz, open(subtitle['SubFileName'], 'wb') as f:
        f.write(gz.read())
    os.remove(tempfile)


def rename_subtitle(vid_filename, sub_filename):
    print "Renaming subtitle %s..." % sub_filename
    vid_name = path.splitext(vid_filename)[0]
    sub_ext = path.splitext(sub_filename)[1]
    name = vid_name + sub_ext
    os.rename(sub_filename, name)


def usage():
    import sys
    print "%s <filename> [<langid>]" % sys.argv[0]


def main():
    import sys
    if len(sys.argv) < 2:
        usage()
        return
    filename = sys.argv[1]
    langid = config.get('Language', 'langid')
    if len(sys.argv) >= 3:
        langid = sys.argv[2]
    subtitle = find_subtitles(filename, langid)[0]
    download_subtitle(subtitle)
    rename_subtitle(filename, subtitle['SubFileName'])


if __name__ == '__main__':
    main()
