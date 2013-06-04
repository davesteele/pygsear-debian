# pygsear
# Copyright (C) 2003 Lee Harr
#
#
# This file is part of pygsear.
#
# pygsear is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pygsear is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pygsear; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Utility script for creating and syncing docs and distribitions"""


import os
import shutil
import glob

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-e", "--epydoc",
                    dest="epydoc",
                    action="store_true",
                    default=False,
                    help="run epydoc to update the local docs")
parser.add_option("-t", "--html",
                    dest="html",
                    action="store_true",
                    default=False,
                    help="copy local docs in to sav_html directory")
parser.add_option("-d", "--dist",
                    dest="dist",
                    action="store_true",
                    default=False,
                    help="create distribution dir in sav_upload dir and copy distfiles")
parser.add_option("-c", "--cvs-sync",
                    dest="cvsync",
                    action="store_true",
                    default=False,
                    help="sync sav_html cvs records with actual files")
parser.add_option("-n", "--no-action",
                    dest="noaction",
                    action="store_true",
                    default=False,
                    help="do not actually run any commands, just show what would be run")

(options, args) = parser.parse_args()


cvs = '/home/lee/python/pygsear-dev/pygsear'
sav_html = '/home/lee/python/pygsear-dev-html/pygsear'
#/usr/home/lee/python/pygame/sav_html/non-gnu/pygsear
sav_upload = '/home/lee/python/pygsear-dev-upload'

lib = 'pygsear'
api_src = os.path.join(cvs, lib)

doc = 'doc'
cvs_doc = os.path.join(cvs, doc)
sav_doc = os.path.join(sav_html, doc)

api_doc = 'api_html'
cvs_api = os.path.join(cvs_doc, api_doc)
sav_api = os.path.join(sav_doc, api_doc)


if options.epydoc:
    print 'running epydoc to update local docs'
    epydoc_comm = 'epydoc -o %s %s/*.py' % (cvs_api, api_src)

    if not options.noaction:
        if os.path.exists(cvs_api):
            shutil.rmtree(cvs_api)
        os.system(epydoc_comm)
    else:
        print epydoc_comm

if options.html:
    print 'copying local docs to sav_html directory'
    html_ignore = os.path.join(cvs_doc, 'html_exclude')
    rsync_comm = 'rsync -v --delete --exclude-from %s -C -r %s/* %s/' % (html_ignore, cvs_doc, sav_doc)

    if not options.noaction:
        os.system(rsync_comm)
    else:
        print rsync_comm

if options.dist:
    print 'creating distribution dir in sav_upload and copying distfiles'
    dist = 'dist'
    cvs_dist = os.path.join(cvs, dist)

    import pygsear
    pygs, ver = pygsear.version().split('-')

    major_ver = os.path.join(sav_upload, 'pygsear-0.pkg')
    sav_ver = os.path.join(major_ver, ver)
    if not os.path.exists(sav_ver) and os.path.exists(cvs_dist):
        if not options.noaction:
            os.mkdir(sav_ver)
        else:
            print 'mkdir', sav_ver

        os.chdir(cvs_dist)
        archs = glob.glob('*%s*' % ver)
        for arch in archs:
            if not arch.endswith('.md5'):
                md5 = '%s.md5' % arch
                md5_comm = 'md5 %s > %s' % (arch, md5)

                if not options.noaction:
                    os.system(md5_comm)
                else:
                    print md5_comm

        rsync_comm = 'rsync -v -C %s/* %s/' % (cvs_dist, sav_ver)

        if not options.noaction:
            os.system(rsync_comm)
        else:
            print rsync_comm

    else:
        print 'No distribution OR distribution dir exists... not copying.'


if options.cvsync:
    print 'synchronizing sav_html cvs records with actual files'
    for dirpath, dirnames, filenames in os.walk(sav_html):
        if 'CVS' in dirnames:
            print
            print dirpath
            os.chdir(dirpath)

            Entries = file(os.path.join(dirpath, 'CVS', 'Entries')).readlines()
            entries = []
            for line in Entries:
                try:
                    d, entry = line.split('/')[:2]
                except ValueError:
                    pass
                else:
                    if not d:
                        entries.append(entry)
                        if not os.path.exists(os.path.join(dirpath, entry)):
                            remove_comm = 'cvs -q remove %s' % entry

                            if not options.noaction:
                                if not os.system(remove_comm):
                                    print 'removed', entry
                                else:
                                    print 'FAILED removing', entry
                            else:
                                print remove_comm

            for filename in filenames:
                if not filename in entries:
                    add_comm = 'cvs add %s' % filename
                    if filename.endswith('.png') or filename.endswith('.jpg'):
                        flags = '-kb'
                    else:
                        flags = ''
                    add_comm = 'cvs -q add %s %s' % (flags, filename)

                    if not options.noaction:
                        if not os.system(add_comm):
                            print 'added', filename
                        else:
                            print 'FAILED adding', filename
                    else:
                        print add_comm

    print
    print 'committing changes to cvs'
    commit_comm = 'cvs commit -m "removing unused docs and adding new docs"'
    if not options.noaction:
        os.chdir(sav_html)
        os.system(commit_comm)
    else:
        print 'chdir', sav_html
        print commit_comm



