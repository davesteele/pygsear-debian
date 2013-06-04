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

from pygsear.Game import Game
from pygsear.Drawable import Circle
from pygsear.locals import BLUE, GREEN
from pygsear.Path import SquarePath


class Dot(Circle):
    def __init__(self):
        Circle.__init__(self, color=GREEN)
        self.get_big = 1
        self.dx = 5

    def move(self):
        if self.get_big:
            if self.rect.w > 100:
                self.get_big = 0
                self.dx = -5

        else:
            if self.rect.w < 20:
                self.get_big = 1
                self.dx = 5

        self.stretch(dx=self.dx, keepAspectRatio=1)

        Circle.move(self)


class Game01(Game):
    def initialize(self):
        self.set_background(color=BLUE)

        thing = Dot()
        path = SquarePath(duration=10)
        path.set_loop(-1)
        thing.set_path(path)
        self.sprites.add(thing)


def main():
    g = Game01()
    g.mainloop()


if __name__ == '__main__':
    main()

