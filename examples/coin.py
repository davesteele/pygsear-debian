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

from pygame.locals import K_SPACE, K_RETURN

from pygsear import Game, Drawable, Event
from pygsear import conf


class Coin(Drawable.MultiImage):
    def __init__(self):
        Drawable.MultiImage.__init__(self, filenames=('coin_front.png', 'coin_back.png'))
        self.center()

    def heads(self, ev=None):
        self.flip('coin_front.png')

    def tails(self, ev=None):
        self.flip('coin_back.png')


class Label(Drawable.String):
    def __init__(self, side):
        Drawable.String.__init__(self, message=side, fontSize=40)
        self.center(dy=150)


class CoinGame(Game.Game):
    def initialize(self):
        self.set_background(color=(95, 25, 123))

        self.coin = Coin()
        self.sprites.add(self.coin)

        self.label_heads = Label('Heads!')
        self.label_tails = Label('Tails!')
        self.label = self.label_heads
        self.sprites.add(self.label)

        self.events.add(Event.KEYUP_Event(key=K_SPACE, callback=self.flipper))
        self.events.add(Event.KEYUP_Event(key=K_RETURN, callback=self.toggle_quick))

        self.autoflip = Event.TIMEOUT_Event(3000, count=-1, callback=self.flipper)
        self.events.add(self.autoflip)

        self.freeze_x = self.freeze_y = 0
        self.quickflip = False

    def restart(self):
        self.set_background(color=(95, 25, 123))
        self.freeze_x = self.freeze_y = 0

    def toggle_quick(self, ev=None):
        self.autoflip.kill()

        self.quickflip = not self.quickflip
        if self.quickflip:
            self.autoflip = Event.TIMEOUT_Event(300, count=-1, callback=self.flipper)
        else:
            self.autoflip = Event.TIMEOUT_Event(3000, count=-1, callback=self.flipper)

        self.events.add(self.autoflip)

    def show_heads(self, ev=None):
        self.coin.heads()
        self.label.kill()
        self.label = self.label_heads

    def show_tails(self, ev=None):
        self.coin.tails()
        self.label.kill()
        self.label = self.label_tails

    def update_label(self):
        self.sprites.add(self.label)

    def freeze_one(self):
        OFFSET = 100

        coin = Drawable.Image(image=self.coin.image)
        coin.set_position((self.freeze_x, self.freeze_y))
        if not coin.onscreen(50):
            self.restart()
            coin.set_position((self.freeze_x, self.freeze_y))
        frozen = Drawable.Stationary(sprite=coin)
        frozen.draw()

        self.freeze_x += OFFSET
        if self.freeze_x > conf.WINWIDTH - self.coin.image.get_width():
            self.freeze_x = 0
            self.freeze_y += OFFSET


    def flipper(self, ev=None):
        if self.quickflip:
            self.flip_coin()
        else:
            ti = 0
            dt = 5
            t = 100
            sides = [self.show_heads, self.show_tails]
            side = 0
            while t < 500:
                self.events.add(Event.TIMEOUT_Event(t, callback=sides[side]))
                t += ti * ti * dt
                ti += .1
                side = not side

            self.events.add(Event.TIMEOUT_Event(t, callback=self.flip_coin))

        self.autoflip.reset()

    def flip_coin(self, ev=None):
        possibilities = [self.show_heads, self.show_tails]
        result = random.choice(possibilities)
        result()
        self.update_label()
        self.freeze_one()


if __name__ == '__main__':
    game = CoinGame()
    game.mainloop()

