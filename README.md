OsDown
======

A script that downloads subtitles from opensubtitles automatically for a given language

Requirements
============

  * Requires the *python-opensubtitles* module which can be found at: https://github.com/agonzalezro/python-opensubtitles
  * Requires the *rarfile* module which you can install with `pip install rarfile`
  * Requires the *unrar* executable for your platform if you want to use the RAR extraction capabilities

Usage
=====
First, edit the osdown.cfg file and add your username and password in the Login section.
You can also select your default language id (currently set to heb - for hebrew)
When running 'python osdown.py <filepath>' the script will download the first subtitle found.
