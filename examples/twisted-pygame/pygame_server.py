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

import time

from pygsear.Network import reactor
import twisted.internet.app
from twisted.cred.authorizer import DefaultAuthorizer
from twisted.spread import pb
from twisted.internet import defer
from twisted.python import log

class PygameServerError(pb.Error):
    """Something went wrong in the PygameServer"""
    pass

class PygameServer:
    def __init__(self):
        self.players = []
        self.playerGames = {}
    def addPlayer(self):
        self.numPlayers += 1
    def gameIsOver(self):
        return 0

    def takePlayerGame(self, playerGame, playerName):
        log.msg('receiving traveler from '+str(playerName))
        self.playerGames[playerName] = playerGame
        if len(self.playerGames) == 2:
            self.makeTravelers()
    def makeTravelers(self):
        log.msg('making travelers')
        for playerGame in self.playerGames.values():
            log.msg('make traveler for %s' % playerGame)
            d = playerGame.callRemote('makeTraveler')
            d.addCallback(self.moveTravelers)
    def dropPlayerGame(self, playerName):
        log.msg('dropping game %s' %playerName)
        del self.playerGames[playerName]
    def moveTravelers(self, dum=None):
        #time.sleep(1)
        for playerGame in self.playerGames.values():
            #log.msg('calling move() on player '+str(playerGame))
            playerGame.callRemote('move')
        d = defer.Deferred()
        d.addCallback(self.moveTravelers)
        d.set_timeout(0, self.moveTravelers)

class Player(pb.Perspective):
    def __init__(self, playerName, identityName="Nobody"):
        pb.Perspective.__init__(self, playerName, identityName)
        self.playerName = playerName
    def set_server(self, server):
        self.server = server
        server.players.append(self)

    def attached(self, clientref, identity):
        print "player '%s' joining game" % identity.name
        self.identity = identity
        #self.server.addPlayer()
        return self
    def detached(self, clientref, identity):
        self.server.dropPlayerGame(self.playerName)

    def perspective_takePlayerGame(self, game):
        log.msg('takePlayerGame called')
        return self.server.takePlayerGame(game, self.playerName)
    def perspective_makeTraveler(self):
        log.msg('makeTraveler called')
        return self.server.makeTraveler()
    #def perspective_moveTraveler(self):
    #    log.msg('moveTraveler called')
    #    return self.game.moveTraveler(self.playerName)


class PygameService(pb.Service):
    def __init__(self, serviceName, serviceParent=None, authorizer=None,
                 application=None):
        pb.Service.__init__(self, serviceName, serviceParent, authorizer,
                            application)
        log.msg('making game')
        self.server = PygameServer()

    def get_perspectiveRequest(self, name):
        log.msg('trying to get perspective for: ' + str(name))
        log.msg('service'+str(self))
        player = Player(name)
        player.set_server(self.server)
        log.msg('player'+str(player))
        return defer.succeed(player)

def setup_players(auth, players):
    for (name, pw) in players:
        i = auth.createIdentity(name)
        i.set_password(pw)
        i.addKeyByString("pygameservice", name)
        auth.addIdentity(i)


def main():
    log.msg('******STARTING******')
    app = twisted.internet.app.Application("pygame_server")
    auth = DefaultAuthorizer(app)
    service = PygameService("pygameservice", app, auth)
    players = [["alice", "sekrit"],
               ["bob", "b0b"],
               ["charlie", "chuck"],
               ["david", "password"],
               ]
    setup_players(auth, players)

    # start the application
    app.listenTCP(8800, pb.BrokerFactory(pb.AuthRoot(auth)))
    app.run()

if __name__ == '__main__':
    main()
