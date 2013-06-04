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


class GG(Game):
    def initialize(self):
        self.set_background(color=BLUE)

        self.thing = Circle(color=GREEN)
        self.thing.center()
        self.thing.path.set_velocity(vx=50)
        self.thing.path.turn_right()
        self.sprites.add(self.thing)


def main():
    g = GG()
    g.mainloop()


if __name__ == '__main__':
    main()

