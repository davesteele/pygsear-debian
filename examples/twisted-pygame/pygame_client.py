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

import sys, re
import random

from pygsear.Network import reactor
from twisted.internet import defer
from twisted.internet.stdio import StandardIO
from twisted.spread import pb
from twisted.protocols.basic import LineReceiver
from pygame_server import PygameServerError
from twisted.python import log

sys.path.append('/mnt/home/missive/python/pygame/simple')
import pygame
from pygame.locals import *
from pygsear import Game
from pygsear import Drawable
from pygsear import Path
from pygsear import conf


class NetGame(pb.Referenceable, Game.Game):
    def checkEvents(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.quit = 1
                reactor.stop()
            elif e.type == KEYUP and e.key == K_ESCAPE:
                self.quit = 1
                reactor.stop()

    def initialize(self):
        self.set_background()
        self.clock = pygame.time.Clock()
        self.x = 0
        self.traveler = None
        self.player = Player("bob", "b0b", self.window, self)

    def addTraveler(self, dum=None, traveler=None):
        if self.traveler is None:
            log.msg('traveler added to game')
            self.traveler = Traveler()
            self.sprites.add(self.traveler)
        else:
            pass
            log.msg('addTraveler called with %s and %s' % dum, traveler)

    def mainloop(self, dum=None):
        log.msg('looping' + str(self.x))
        #log.msg('clearing')
        #self.clearSprites()
        #log.msg('checking')
        self.checkEvents()
        #log.msg('moving')
        #self.moveSprites()
        d = defer.Deferred()
        d.addCallback(self.mainloop)
        d.callback()
        self.x += 1

    def error(self):
        log.msg('error, stopping reactor')
        reactor.stop()

class Traveler(Drawable.Circle):
    def __init__(self):
        Drawable.Circle.__init__(self)
        path = Path.CirclePath()
        path.set_loop(-1)
        self.set_path(path)

    def requestMove(self):
        d = self.p.callRemote('moveTraveler')
        d.addCallback(self.game.mainloop)

    def remote_move(self):
        #log.msg('remote_move called')
        self.uclear()
        Drawable.Circle.move(self)
        self.udraw()

class Player:
    def __init__(self, name, passwd, w, game):
        log.msg('initializing %s' % name)
        self.p = None
        self.w = w
        self.game = game
        self.connect(name, passwd)

    def connect(self, name, passwd):
        self.d = pb.connect("localhost",
                                8800, name, passwd, "pygameservice")
        self.d.addCallback(self.join)
        self.d.addErrback(self.join_failed)
        self.d.addCallback(self.givePlayerGame)

    def join(self, perspective):
        self.p = perspective
        #log.msg(" game joined")

    def join_failed(self, why):
        t = why.type
        #print "t", t, type(t)
        #print "check", why.check(PygameServerError)
        #print " failed:", why.get_errorMessage()
        reactor.stop()

    def givePlayerGame(self, dum=None):
        #log.msg('giveTraveler called')
        #traveler = Traveler(self.p, self.w, self.game)
        #self.game.addTraveler(traveler=traveler)
        d = self.p.callRemote('takePlayerGame', self.game)
        d.addCallback(self.game.mainloop)

    def noTraveler(self, d):
        pass
        #log.msg('must pass Traveler before foo ing')
        #log.msg('received: ' + str(d))

    def goTraveler(self):
        self.p.callRemote('moveTraveler')


def main():
    g = NetGame()

    reactor.run()


if __name__ == '__main__':
    main()

