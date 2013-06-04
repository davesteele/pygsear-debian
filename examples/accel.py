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

from pygsear import Game, Drawable, Event, conf
from pygsear.Util import color

BLUE = color('blue')
RED = color('red')



class C2(Drawable.Circle):
    def __init__(self):
        Drawable.Circle.__init__(self, color='random')
        self.path.set_restriction(onscreen=1,
                                    speed=100,
                                    xMax=conf.WINWIDTH-30,
                                    yMax=conf.WINHEIGHT-30,
                                    )
        self.center()
        self.path.set_velocity(vx=0.1, vy=0.1)
        self.set_turn()
        self.set_acc()

    def set_turn(self, ev=None):
        path = self.path
        left = path.turn_left
        right = path.turn_right
        straight = path.turn_straight

        choices = [(left, 1000, 3000), (straight, 1000, 3000), (right, 1000, 3000)]
        #choices = [(right, 100, 300)]

        turn, tmin, tmax = random.choice(choices)
        turn()

        timeout = random.randrange(tmin, tmax)
        conf.game.events.add(Event.TIMEOUT_Event(timeout, callback=self.set_acc))

    def set_acc(self, ev=None):
        a = random.randrange(-50, 120)
        if a < 0:
            self.path.decelerate(a)
            #self.set_color(BLUE)
            #self.set_color(r=0, b=-a*3, g=0)
        else:
            self.path.accelerate(a)
            #self.set_color(RED)
            #self.set_color(r=a*2, b=0, g=0)

        timeout = random.randrange(100, 1000)
        conf.game.events.add(Event.TIMEOUT_Event(timeout, callback=self.set_acc))


class AccelGame(Game.Game):
    def checkCollisions(self):
        if self.tot_time < 500:
            self.tot_time += conf.ticks
        else:
            raw = self.clock.get_rawtime()
            maxfps = conf.MAX_FPS
            #print raw, maxfps
            if raw < maxfps:
                #print 'dot'
                self.make_dot()
                self.tot_time = 0

    def make_dot(self):
        dot = C2()
        self.sprites.add(dot)


    def initialize(self):
        self.set_background(color=(95, 0, 0))
        self.make_dot()
        self.tot_time = 0


if __name__ == '__main__':
    game = AccelGame()
    game.mainloop()

