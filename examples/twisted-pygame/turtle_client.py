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


from pygsear.Network import reactor

from pygsear.Game import TwistedGame
from pygsear.Drawable import Turtle
from pygsear.Network import TwoPlayerConnection



class Connection(TwoPlayerConnection):
    def forward(self, distance):
        self.connection.callRemote('forward', distance)

    def right(self, deg):
        self.connection.callRemote('right', deg)


class LTurtleGame:
    def __init__(self, reactor, host, port):
        self.host = host
        self.port = port
        self.reactor = reactor
        self.initialize()

    def initialize(self):
        self.connection = Connection(self)
        self.reactor.callLater(1, self.m1)

    def m1(self):
        self.connection.forward(100)
        self.reactor.callLater(1, self.m2)

    def m2(self):
        self.connection.right(90)
        self.reactor.callLater(1, self.m1)

    def mainloop(self):
        """The main twisted game loop."""

        self.reactor.callLater(0.1, self.mainloop)



if __name__ == '__main__':
    game = LTurtleGame(reactor=reactor, host='localhost', port=11223)
    game.mainloop()
    reactor.run()


