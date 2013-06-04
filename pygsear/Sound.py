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


"""Sounds"""

import pygame

import Util
import conf


class DummySound:
    """Mock sound object, for when sound is not working.

    If L{Util.load_sound} sees that the sound is not working, it
    will only hand out these mock objects which support all of the
    same methods as L{pygame.mixer.Sound} objects, but which make
    no calls in to the actual sound system.

    """

    def fadeout(self, millisec):
        pass

    def get_num_channels(self):
        return 0

    def get_volume(self):
        return 0

    def play(self, loops=None, maxtime=None):
        pass

    def set_volume(self, val):
        pass

    def stop(self):
        pass


def check_sound():
    """Test the sound system by trying to play a sound.

    Stores the status of the sound system in C{conf.sound_status}

    """

    dirs = Util.get_dirs('sounds')
    test_sound = Util.get_full_path('test_sound.wav', dirs)
    try:
        sound = pygame.mixer.Sound(test_sound)
        sound.play()
        conf.sound_status = 'OK'
    except:
        conf.sound_status = 'FAILED'



def pause():
    """Pause the sound playback, if sound is working"""

    if conf.sound_status == 'OK':
        pygame.mixer.pause()

def unpause():
    """Unpause the sound playback, if sound is working"""

    if conf.sound_status == 'OK':
        pygame.mixer.unpause()


