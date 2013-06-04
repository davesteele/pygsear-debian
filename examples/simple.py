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

import time, random, math

import pygame
import pygame.draw

from pygsear import Game, Drawable, Path, Cursor, conf
from pygsear.locals import TRANSPARENT2, PIx2

class SimpleGame(Game.Game):
    def initialize(self):
        self.set_background(tilename='sky.png')
        self.hideMouse()


        alien2 = Drawable.Image(filename='alien2.png', alpha=100)
        path2 = Path.LinePath(startLocation=(250, 250),
                                endLocation=(400, 400),
                                duration=3,
                                steps=80)
        path2.set_loop(-1)
        alien2.set_path(path2)
        self.sprites.add(alien2)



        alien3 = Drawable.Image(filename='alien3.png')
        path3 = Path.BounceLinePath(startLocation=(350, 350),
                                        endLocation=(100, 100),
                                        duration=10,
                                        steps=250)
        path3.set_loop(-1)
        alien3.set_path(path3)
        self.sprites.add(alien3)



        alien4 = Drawable.Image(filename='alien_alpha.png',
                                colorkey=None, alpha=1)
        path4 = Path.RandomAccelerationPathBounded(startLocation=(400, 400),
                            startDirection=1,
                            startSpeed=0,
                            duration=None,
                            maxSpeed=20,
                            maxAccel=3)
        alien4.set_path(path4)
        self.sprites.add(alien4)



        num = Drawable.String(message='$^#&^#$', fontSize=70)
        path = Path.CirclePath(startLocation=(275, 275),
                                startDirection=3.14,
                                duration=5,
                                size=40,
                                steps=200,
                                clockwise=0)
        path.set_loop(-1)
        num.set_path(path)
        self.sprites.add(num)



        swirl = Drawable.AnimatedImage(dirname='swirl', colorkey=TRANSPARENT2)
        path = Path.FilePath('path', duration=8)
        path.set_loop(-1)
        swirl.set_path(path)
        self.sprites.add(swirl)



        purple = Drawable.AnimatedImage(filenames=['purpleThrob/purple0.png',
                                        'purpleThrob/purple1.png',
                                        'purpleThrob/purple2.png',
                                        'purpleThrob/purple3.png',
                                        'purpleThrob/purple4.png',
                                        'purpleThrob/purple3.png',
                                        'purpleThrob/purple2.png',
                                        'purpleThrob/purple1.png'])
        path = Path.Offset_path(path3, 60, 60)
        purple.set_path(path)
        self.sprites.add(purple)



        multi = Drawable.Multi()
        one = Drawable.Circle()
        two = Drawable.Circle(radius=20)
        multi.addSprite(one)
        multi.addSprite(two, 40, 40)
        path = Path.BounceCirclePath(duration=11)
        path.set_loop(-1)
        multi.set_path(path)
        self.sprites.add(multi)



        direct = Drawable.MultiImage(dirname='arrow', defaultImage='right.png')
        path = Path.SquareEightPath(duration=20)
        path.set_loop(-1)
        direct.set_path(path)
        self.direct = direct
        self.sprites.add(direct)
        direct.oldDirection = direct.path.get_direction()



        cursor = Cursor.XCursor(self.window, 11)
        self.sprites.add(cursor, level=1)


    def checkCollisions(self):
        directNewDirection = self.direct.path.get_direction()
        if directNewDirection != self.direct.oldDirection:
            direction = directNewDirection % PIx2
            self.direct.oldDirection = direction
            if direction < 0.1 or direction > PIx2-0.1:
                self.direct.flip('right.png')
            elif 4.5 < direction < 4.8:
                self.direct.flip('down.png')
            elif 3.0 < direction < 3.2:
                self.direct.flip('left.png')
            else:
                self.direct.flip('up.png')


def main():
    g = SimpleGame()
    g.mainloop()

if __name__ == '__main__':
    main()


