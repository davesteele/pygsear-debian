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

import random

import pygame

from pygsear import Game, Drawable, Path, conf
from pygsear.locals import *


class Wing(Drawable.RotatedImage):
    def __init__(self, name):
        self.name = name
        Drawable.RotatedImage.__init__(self, filename='arrow/right.png', steps=36)
        p = Path.RandomAccelerationPathBounded(minSpeed=2)
        self.set_path(p)
        self.center()

    def move(self):
        self.set_rotation(self.path.get_direction())
        Drawable.RotatedImage.move(self)


class Ship(Drawable.RotatedImage):
    def __init__(self):
        Drawable.RotatedImage.__init__(self, filename='penguin2.png', steps=36)
        self.path.set_speed(100)
        self.set_position((50, 50))

    def set_enemy(self, enemy):
        self.enemy = enemy

    def follow_enemy(self):
        self.path.turn_towards(self.enemy.get_position())

    def move(self):
        self.follow_enemy()
        self.set_rotation(self.path.get_direction())
        Drawable.RotatedImage.move(self)


class AGame(Game.Game):
    def initialize(self):
        self.makeWings()
        self.makeShip()

    def makeWings(self):
        self.enemies = self.addGroup()
        for name in ['Kirk', 'Spock', 'McCoy', 'Scotty', 'Chekov']:
            i = Wing(name)
            self.sprites.add(i)
            self.enemies.add(i)

    def makeShip(self):
        self.ship = Ship()
        self.sprites.add(self.ship)
        self.chooseEnemy()

    def chooseEnemy(self):
        enemy = random.choice(self.enemies.sprites())
        self.ship.set_enemy(enemy)

        if hasattr(self, 'message'):
            self.message.clear()
        message = Drawable.String(message='"I am for %s"' % enemy.name,
                                        fontSize=30)
        message.center()
        self.message = Drawable.Stationary(sprite=message)
        self.message.draw()

    def checkCollisions(self):
        if self.ship.collide(self.ship.enemy):
            self.ship.enemy.kill()
            if not len(self.enemies.sprites()):
                self.makeWings()
            self.chooseEnemy()


if __name__ == '__main__':
    g = AGame()
    g.mainloop()
