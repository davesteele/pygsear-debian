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
    def __init__(self):
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

    def set_blocks(self, blocks):
        self.blocks = blocks

    def follow_enemy(self):
        if self.can_see(self.enemy, self.blocks):
            self.path.turn_towards(self.enemy.get_position())
        else:
            self.path.turn_right()


    def move(self):
        self.follow_enemy()
        self.set_rotation(self.path.get_direction())
        Drawable.RotatedImage.move(self)


class Block(Drawable.Rectangle):
    def __init__(self):
        Drawable.Rectangle.__init__(self, width=100, height=10)
        self.set_positionRandom()
        sblock = Drawable.Stationary(sprite=self)
        sblock.draw()


class AGame(Game.Game):
    def initialize(self):
        Game.Game.initialize(self)
        self.makeBlocks()
        self.makeWings()
        self.makeShip()

        # this is a weird hack... probably should
        # not be doing it like this.
        Game.SpriteGroup.draw = Game.SpriteGroup.draw_visible

    def makeBlocks(self):
        self.blocks = []
        for b in range(5):
            block = Block()
            self.blocks.append(block.crect)

    def makeWings(self):
        self.enemies = self.addGroup()
        for name in range(5):
            i = Wing()
            self.sprites.add(i)
            self.enemies.add(i)

    def makeShip(self):
        self.ship = Ship()
        self.ship.set_blocks(self.blocks)
        self.sprites.add(self.ship)
        self.chooseEnemy()
        self.ship.hidden = 0

    def chooseEnemy(self):
        enemy = random.choice(self.enemies.sprites())
        self.ship.set_enemy(enemy)

    def checkCollisions(self):
        if self.ship.collide(self.ship.enemy):
            self.ship.enemy.kill()
            if not len(self.enemies.sprites()):
                self.makeWings()
            self.chooseEnemy()

        for enemy in self.enemies.sprites():
            if not self.ship.can_see(enemy, self.blocks):
                enemy.hidden = 1
            else:
                enemy.hidden = 0


if __name__ == '__main__':
    g = AGame()
    g.mainloop()
