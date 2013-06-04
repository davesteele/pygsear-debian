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

from pygsear import Game, Drawable, Path


class Wing(Drawable.RotatedImage):
    def __init__(self):
        Drawable.RotatedImage.__init__(self, filename='arrow/right.png', steps=36)
        p = Path.RandomAccelerationPathBounded(minSpeed=2)
        self.set_path(p)
        self.center()

        self.stretch(dx=50, keepAspectRatio=0)

    def move(self):
        self.set_rotation(self.path.get_direction())
        Drawable.RotatedImage.move(self)


class AGame(Game.Game):
    def initialize(self):
        self.makeWings()

    def makeWings(self):
        for thing in range(5):
            i = Wing()
            self.sprites.add(i)


g = AGame()
g.mainloop()

