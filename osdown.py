#!/usr/bin/env python

########## Imports

from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File

import ConfigParser
from numbers import Number

import gzip
import rarfile
import zipfile

from tempfile import mktemp
import os
from os import path
import urllib


########## Constants

RAR_EXT = [ ".rar" ]
ZIP_EXT = [ ".zip" ]

COMPRESSED_EXTS = RAR_EXT + ZIP_EXT
VID_EXTS = [ ".avi", ".h264", ".hdmov", ".mkv", ".mov", ".mp4", ".ogv", ".xvid" ]


########## Configuration and setup

config = ConfigParser.RawConfigParser()
config.read(os.path.realpath(__file__)[:-2] + 'cfg')
osmgr = OpenSubtitles()
osmgr.login(config.get('Login', 'user'), config.get('Login', 'pass'))


########## Main functions

def download_subtitle(subtitle):
    print 'Downloading %s...' % subtitle['SubFileName']
    tempfile = mktemp()
    urllib.urlretrieve(subtitle['SubDownloadLink'], tempfile)
    with gzip.open(tempfile, 'rb') as gz, open(subtitle['SubFileName'], 'wb') as f:
        f.write(gz.read())
    os.remove(tempfile)


def extract_videos(compressed_file):
    # Select the right API to extract the files out of the archive.
    klass = extract_dict[file_ext(compressed_file)]
    archive = klass(compressed_file)
    videos = [video for video in archive.namelist() if file_ext(video) in VID_EXTS]
    print "Extracting videos (using %s) %s..." % (str(klass), ", ".join(videos))
    map(archive.extract, videos, ["."] * len(videos))
    return videos


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


def main():
    import sys
    if len(sys.argv) < 2:
        usage()
        return
    filename = sys.argv[1]
    langid = config.get('Language', 'langid')
    if len(sys.argv) >= 3:
        langid = sys.argv[2]
    if file_ext(filename) in COMPRESSED_EXTS:
        videos = extract_videos(filename)
        map(process_subtitle, videos, [langid] * len(videos))
    else:
        process_subtitle(filename, langid)


def process_subtitle(filename, langid):
    subtitle = find_subtitles(filename, langid)[0]
    download_subtitle(subtitle)
    rename_subtitle(filename, subtitle['SubFileName'])


def rename_subtitle(vid_filename, sub_filename):
    print "Renaming subtitle %s..." % sub_filename
    vid_name = file_name(vid_filename)
    sub_ext = file_ext(sub_filename)
    name = vid_name + sub_ext
    os.rename(sub_filename, name)


########## General Utilities

# Compressed files extraction libraries
extract_class = [ rarfile.RarFile, zipfile.ZipFile ]
extract_dict = dict(zip(COMPRESSED_EXTS, extract_class))


def file_ext(filename):
    return path.splitext(filename)[1]


def file_name(filename):
    return path.splitext(filename)[0]


# Command-line Interface

def usage():
    import sys
    print "%s <filename> [<langid>]" % sys.argv[0]


if __name__ == '__main__':
    main()
