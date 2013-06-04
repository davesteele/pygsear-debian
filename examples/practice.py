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




# ####           INSTRUCTIONS          ####
# ####                                 ####
# ####                                 ####
#
# practice.py
#
# pygsear game for practicing moving around with the turtle-graphics commands.
# To play, run the program and use the four basic turtle commands:
#
# forward(N)
# backward(N)
# right(N) and
# left(N)
#
# where N is a number you choose.
#
# With forward() and backward() N is the number of pixels to move.
# With right() and left() N is the number of degrees to turn.
#
# Try to move pete on to the target.
# You get 10 moves to hit 5 targets.
# Turning does not count as a move.


import random
import os

from pygame.time import wait
from pygame.locals import K_ESCAPE, K_F8

from pygsear import conf
from pygsear import Drawable
from pygsear import Widget
from pygsear import Event
from pygsear.Game import Game
from pygsear.Path import RandomOnscreen
from pygsear.Path import CirclePath
from pygsear.locals import GREEN


from interact import InteractPenguin, TurtleConsole

class Target(Drawable.Stationary):
    def __init__(self, w=None):
        i = Drawable.Image(filename='target.png')
        Drawable.Stationary.__init__(self, sprite=i)
        self.poof()

    def poof(self):
        x = random.randrange(50, conf.WINWIDTH-114)
        y = random.randrange(50, conf.WINHEIGHT-364)
        self.set_position((x, y))


class Score(Drawable.Stationary):
    def __init__(self, pos=(100,100), label=''):
        self.score = Widget.Score(position=pos, text=label, color=GREEN)
        Drawable.Stationary.__init__(self, sprite=self.score)

    def addPoints(self, p):
        self.clear()
        self.score.addPoints(p)
        self.score.updateScore()
        self.prepare()
        self.draw()


class Player(InteractPenguin):
    pass


class PracticeGame(Game):
    def initialize(self):
        Game.initialize(self)
        self.set_background(color=(50, 90, 130))
        self.target = Target()
        #self.target.draw()
        self.count = Score(pos=(20, 30), label='Targets:')
        self.count.addPoints(5)
        self.score = Score(pos=(20, 60), label='Moves:')
        self.score.addPoints(10)
        self.player = InteractPenguin()
        self.player.penUp()
        self.sprites.add(self.player)
        self.moveTarget()

    def moveTarget(self):
        self.target.poof()
        while self.player.rect.colliderect(self.target.rect):
            self.target.poof()

    def message(self, m):
        t = Drawable.String(self.window, m)
        p = CirclePath(duration=10)
        t.set_path(p)
        try:
            t.runPath()
        except:
            pass
        wait(2000)
        os._exit(0)

    def win(self):
        self.message('YOU WIN !')

    def lose(self):
        self.message('YOU LOSE !')

    def forward(self, dist):
        self.player.forward(dist)
        self.score.addPoints(-1)
        if not self.score.score.points:
            self.lose()
        self.mainloop(1)
        if self.player.rect.colliderect(self.target.rect):
            self.count.addPoints(-1)
            self.player.blink(5)
            if not self.count.score.points:
                self.win()
            self.moveTarget()
            self.mainloop(1)

    def backward(self, dist):
        self.forward(-dist)


class Console(TurtleConsole):
    def set_modal_events(self):
        self.quit_ev = Event.QUIT_Event(callback=self._quit)
        self.events.add(self.quit_ev)
        self.stop_ev = Event.KEYUP_Event(key=K_ESCAPE, callback=self.toggle_visible)
        self.events.add(self.stop_ev)
        quit_ev2 = Event.KEYUP_Event(key=K_F8, callback=self._quit)
        self.events.add(quit_ev2)


    def greeting(self):
        self.new_line('Press ESC to show/hide console')
        self.new_line('Press F8 to QUIT')
        self.new_line('')
        self.new_line('forward(N), backward(N), right(N), left(N) to move around...N is any number.')
        self.new_line('Hit the target 5 times to win!  Turning does not count as a move.')


if __name__ == '__main__':
    g = PracticeGame()
    g.mainloop(1)

    loc = {'pete': g.player,

        'forward': g.forward,
        'backward': g.backward,
        'right': g.player.right,
        'left': g.player.left
    }

    interpreter = Console(locals=loc, size=(700, 150))

    interpreter.modal()

