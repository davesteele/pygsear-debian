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

import twisted.internet.app
from twisted.cred.authorizer import DefaultAuthorizer
from twisted.spread import pb
from twisted.internet import defer
from twisted.python import log

import GameBoard

class ServerError(pb.Error):
    """Something went wrong in the Server"""
    pass

class TwistTacToeServer:
    def __init__(self):
        self.playerBoards = {}
        self.gameBoard = GameBoard.GameBoard(6, 4, 3)
        self.players = []
        self.queue = self.gameBoard.queue

    def get_gameInfo(self):
        size = self.gameBoard.size
        toWin = self.gameBoard.toWin
        players = self.players
        queue = self.queue

        gameInfo = {'size': size,
                    'toWin': toWin,
                    'players': self.gameBoard.players,
                    'maxPlayers': self.gameBoard.maxPlayers,
                    'queue': queue,
                    'board': self.gameBoard.board}
        return gameInfo

    def addPlayer(self, player):
        if self.gameBoard.started and len(self.queue) < self.maxPlayers:
            self.queue.append(player)
        else:
            self.players.append(player)
            self.gameBoard.addPlayer(player.name)
    def removePlayer(self, player):
        if player in self.players:
            self.players.remove(player)
            self.gameBoard.removePlayer(player.name)
        elif player in self.queue:
            self.queue.remove(player)
        if not self.players and not self.queue:
            log.msg('** GAME RESET **')
            self.gameBoard.reset_board()
        self.dropPlayerBoard(player)
        self.left(player)
        self.gameOver()
    def joined(self, player):
        for board in self.get_boards():
            board.callRemote('joined', player.name)
    def left(self, player):
        for board in self.get_boards():
            board.callRemote('left', player.name)

    # A playerBoard is the player's "view" of the game
    def takePlayerBoard(self, player, playerBoard):
        log.msg('receiving board from %s' % player)
        self.joined(player)
        self.playerBoards[player] = playerBoard
    def dropPlayerBoard(self, player):
        log.msg('dropping board %s' % player)
        if player in self.playerBoards:
            del self.playerBoards[player]
    def get_boards(self):
        return self.playerBoards.values()

    def startOK(self):
        log.msg('startOK? players: %s' % self.players)
        if len(self.players) > 1:
            ok = 1
        else:
            ok = 0
        for player in self.players:
            if not player.startOK:
                ok = 0
                break
        return ok

    def start(self):
        if self.startOK():
            self.gameBoard.startGame()
            for board in self.get_boards():
                board.callRemote('start')
            self.nextMove()

    def move(self, player, position):
        try:
            self.gameBoard.move(player.name, position)
        except ValueError:
            self.badMove(player)
        else:
            self.goodMove(player, position)

    def badMove(self, player):
        """This should not happen.

        If it does, notify the client, then try to sync client
        state with server state.

        XXX: maybe should sync ALL clients!

        """
        self.playerBoards[player].callRemote('badMove')
        self.playerBoards[player].callRemote('sync', self.gameBoard.board)

    def goodMove(self, player, position):
        "Notify all players of move, and start next move"

        self.showMove(player, position)
        if self.gameBoard.checkGameOver():
            self.gameOver()
        else:
            self.nextMove()

    def showMove(self, player, position):
        for board in self.get_boards():
            log.msg('notifying %s :: %s: %s' % (board,
                                                player.name, position))
            board.callRemote('showMove', player.name, position)

    def nextMove(self):
        nextPlayer = self.gameBoard.get_nextPlayer()
        for player in self.players:
            if player.name == nextPlayer:
                self.playerBoards[player].callRemote('go')
            else:
                self.playerBoards[player].callRemote('wait',
                                                       nextPlayer)

    def gameOver(self):
        over = self.gameBoard.checkGameOver()
        for player in self.players:
            player.startOK = 0
        for board in self.get_boards():
            board.callRemote('gameOver', over)
        self.gameBoard.reset_board()

class TwistTacToePlayer(pb.Perspective):
    """Player perspective on the Twist-Tac-Toe board

    There must only be one player with any particular name.

    """

    playerNames = []

    def __init__(self, name, identityName="Nobody"):
        if name in self.playerNames:
            raise KeyError, "Name already in use: %s" % name
        self.playerNames.append(name)
        pb.Perspective.__init__(self, name, identityName)
        self.name = name
        self.startOK = 0

    def set_server(self, server):
        self.server = server

    def attached(self, clientref, identity):
        log.msg("player '%s' joining game" % identity.name)
        self.identity = identity
        self.server.addPlayer(self)
        return self
    def detached(self, clientref, identity):
        log.msg('player %s detached' % self)
        self.server.removePlayer(self)
        self.playerNames.remove(self.name)

    def perspective_get_gameInfo(self):
        gameInfo = self.server.get_gameInfo()
        log.msg(gameInfo)
        return defer.succeed(gameInfo)
    def perspective_takePlayerBoard(self, board):
        log.msg('takePlayerGame called')
        self.server.takePlayerBoard(self, board)
        return defer.succeed(1)
    def perspective_startGame(self):
        if self in self.server.playerBoards:
            self.startOK = 1
            self.server.start()
        else:
            raise ServerError, "Did not receive player board yet."
    def perspective_move(self, position):
        self.server.move(self, position)


class TwistTacToeService(pb.Service):
    def __init__(self, serviceName, serviceParent=None, authorizer=None,
                 application=None):
        pb.Service.__init__(self, serviceName, serviceParent, authorizer,
                            application)
        log.msg('making game')
        self.server = TwistTacToeServer()

    def get_perspectiveRequest(self, name):
        log.msg('trying to get perspective for: ' + str(name))
        log.msg('service'+str(self))
        player = TwistTacToePlayer(name)
        player.set_server(self.server)
        log.msg('player'+str(player))
        return defer.succeed(player)

def setup_players(auth, players):
    for (name, pw) in players:
        i = auth.createIdentity(name)
        i.set_password(pw)
        i.addKeyByString("TwistTacToeService", name)
        auth.addIdentity(i)


def main():
    log.msg('******STARTING******')
    app = twisted.internet.app.Application("Twist-Tac-Toe")
    auth = DefaultAuthorizer(app)
    service = TwistTacToeService("TwistTacToeService", app, auth)
    players = [["alice", "guest"],
               ["bob", "guest"],
               ["charlie", "guest"],
               ["david", "guest"],
               ["guest0", "guest"],
               ["guest1", "guest"],
               ["guest2", "guest"],
               ["guest3", "guest"],
               ["missive", "guest"],
               ]
    setup_players(auth, players)

    # start the application
    app.listenTCP(8800, pb.BrokerFactory(pb.AuthRoot(auth)))
    app.run()

if __name__ == '__main__':
    main()
