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

import pygame
from pygame.locals import *

from pygsear import Game, Drawable, Path, Widget
from pygsear.locals import *


class G(Game.Game):
    def initialize(self):
        self.set_background(tilename='bg9.png')

        self.input = Widget.TextInput(self.window, text="test",
                            size=30, border=0, group=self.events)
        self.input.set_callback(self.booj)
        self.input.set_position((200, 50))
        self.input.activate()
        self.sprites.add(self.input)

        self.input2 = Widget.TextInput(self.window, text="test",
                            maxLength=15, size=30, border=2)
        self.events.add(self.input2.events)
        self.input2.set_callback(self.booj)
        self.input2.set_position((400, 50))
        self.input2.deactivate()
        self.sprites.add(self.input2)

        self.button = Widget.SpriteTextButton(self.window, "Big Button",
                            size=40, color=RED, padding=20)
        self.events.add(self.button.events)
        self.button.set_callback(self.bang)
        self.button.set_position((200, 100))
        self.sprites.add(self.button)

        b2 = Widget.SpriteButton(Drawable.Image(self.window, 'sky.png'))
        self.events.add(b2.events)
        p = Path.CirclePath(duration=20)
        p.set_loop(-1)
        b2.set_path(p)
        self.b2 = b2
        b2.set_callback(self.stopStart)
        self.sprites.add(b2)
        self.sky = b2

        statButton = Widget.StationaryTextButton(self.window, 'STAT')
        self.events.add(statButton.events)
        statButton.set_position((400,300))
        statButton.set_callback(self.stat)
        statButton.draw()

    def bang(self, ev):
        x, y = self.button.get_position()
        x += 10
        y += 10
        self.button.set_position((x, y))
        self.button.move()
        print 'BANG'

    def stopStart(self, ev):
        if not hasattr(self.sky, 'savedPath'):
            self.sky.savedPath = self.sky.path
            self.sky.savedPath.pause()
            self.sky.set_path(Path.StationaryPath(self.sky))
            self.sky.move()
        else:
            path = self.sky.path
            self.sky.pause()
            self.sky.savedPath.unpause()
            self.sky.set_path(self.sky.savedPath)
            self.sky.savedPath = path

    def booj(self, text):
        print text

    def stat(self, a):
        print 'stat', a

g = G()
g.mainloop()

