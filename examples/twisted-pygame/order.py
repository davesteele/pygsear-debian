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

import time

from twisted.internet.defer import Deferred
from twisted.internet import reactor

def a1(arg):
    print 'sleeping a1', arg
    #time.sleep(11)
    reactor.callLater(1, a2)

def a2(arg=None):
    print 'sleeping a2', arg
    #time.sleep(12)
    reactor.callLater(2, a3)

def a3(arg=None):
    print 'a3', arg
    #time.sleep(13)

def b0(d):
    print 'sleeping 0'
    d.callback(None)

def b1():
    print 'sleeping b1'
    time.sleep(1)
    reactor.callLater(0, b1)


def main():
    d = Deferred()
    d.addCallback(a1)
    #d.addCallback(a2)
    #d.addCallback(a3)
    reactor.callLater(0, b0, d)
    reactor.callLater(1, b1)
    #d.callback(None)

    print 'running'
    reactor.run()

if __name__ == '__main__':
    main()
