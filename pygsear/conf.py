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

"""conf.py can be used as a shared "global" namespace"""

import ConfigParser
import os

MAX_WINWIDTH = 1024
MIN_WINWIDTH = 580
MAX_WINHEIGHT = 768
MIN_WINHEIGHT = 360

configParser = ConfigParser.ConfigParser()
try:
    configParser.read(os.path.expanduser('~/.pygsear/config'))
    WINWIDTH = int(c.get('screen', 'WINWIDTH'))
    WINHEIGHT = int(c.get('screen', 'WINHEIGHT'))
    WINFULL = int(c.get('screen', 'WINFULL'))
except:
    #WINWIDTH = 640
    WINWIDTH = 800
    #WINHEIGHT = 480
    WINHEIGHT = 600
    WINFULL = 0

WINWIDTH = max(WINWIDTH, MIN_WINWIDTH)
WINWIDTH = min(WINWIDTH, MAX_WINWIDTH)
WINHEIGHT = max(WINHEIGHT, MIN_WINHEIGHT)
WINHEIGHT = min(WINHEIGHT, MAX_WINHEIGHT)

WINSIZE = [WINWIDTH, WINHEIGHT]


MAX_FPS = 30
MAX_TICK = 50

ticks = 0

sound_status = None

game = None
