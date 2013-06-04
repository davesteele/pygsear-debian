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

import sys
import os
import time

from twisted.internet import reactor
from twisted.internet import defer
from twisted.spread import pb
from twisted.python import log

from pygsear import conf
conf.WINWIDTH=400
conf.WINHEIGHT=275
conf.WINSIZE=(conf.WINWIDTH, conf.WINHEIGHT)
from pygsear.locals import *
from pygsear import Game, Screen, Event, Drawable, Widget

from GameBoard import GameBoard


class TG(pb.Referenceable, Game.TwistedGame):
    def showBoard(self):
        size = self.board.size
        boardSize = self.boardSize
        px0 = self.px0
        py0 = self.py0

        boxSize = int(boardSize / size)

        for x in range(size):
            for y in range(size):
                pos = (x, y)
                px = px0 + x*boxSize
                py = py0 + y*boxSize
                s = Drawable.Square(side=boxSize-4, color=BLACK)
                s.set_position((px, py))
                stat = Drawable.Stationary(sprite=s)
                stat.draw()
                if pos in self.board.board:
                    name = self.board.board[pos]
                    color = COLORS[self.players.index(name)]
                    c = Drawable.Circle(radius=boxSize-10, color=color)
                    c.set_position((px, py))
                    stat = Drawable.Stationary(sprite=c)
                    stat.draw()

    def set_name(self):
        if len(sys.argv) > 1:
          name = sys.argv[1]
        else:
            try:
                name = os.getlogin()
            except:
                name = 'guest0'
        self.name = name

    def connect(self):
        print 'connecting as', self.name
        d = pb.connect("localhost", 8800, self.name, 'guest',
                             "TwistTacToeService")
        d.addCallback(self.connected)
        d.addErrback(self.connectionFailed)

    def connectionFailed(self, msg):
        if self.name.startswith('guest'):
            n = int(self.name[-1])
            if n < 3:
                n += 1
                self.name = 'guest%s' % n
                self.connect()
            else:
                self.connectionReallyFailed()
        else:
            self.name = 'guest0'
            self.connect()

    def connectionReallyFailed(self):
        log.msg('Connection Failed')
        errMsg = Drawable.String(message='Connection Failed')
        errMsg.set_position((200, 200))
        self.errMsg = Drawable.Stationary(sprite=errMsg)
        self.errMsg.draw()

        if not self.startedServer:
            print 'trying to start server'
            self.startedServer = 1
            os.spawnlp(os.P_NOWAIT, 'python', 'python', 'GameServer.py')
            time.sleep(9)
            self.set_name()
            self.connect()

    def connected(self, perspective):
        print 'ok'
        if hasattr(self, 'errMsg'):
            self.errMsg.uclear()
        self.perspective = perspective
        d = self.perspective.callRemote('get_gameInfo')
        d.addCallback(self.gameSetup)

    def gameSetup(self, gameInfo):
        log.msg('gameInfo: %s' % gameInfo)
        size = gameInfo['size']
        toWin = gameInfo['toWin']
        players = gameInfo['players']
        maxPlayers = gameInfo['maxPlayers']
        queue = gameInfo['queue']
        board = gameInfo['board']

        self.board = GameBoard(size=size, toWin=toWin, maxPlayers=maxPlayers)

        for player in players:
            self.addPlayer(player)
            self.board.addPlayer(player)

        self.showBoard()

        d = self.perspective.callRemote('takePlayerBoard', self)
        d.addCallback(self.whenReady)

    def whenReady(self, one=None):
        restart = Widget.StationaryTextButton(self.window, text='START', group=self.events)
        restart.set_callback(self.reset)
        restart.set_position((conf.WINWIDTH/2, 5))
        restart.draw()
        self.msg2 = restart

    def reset(self, pygameEvent):
        if hasattr(self, 'msg2'):
            self.msg2.clear()
            del(self.msg2)
        self.board.reset_board()
        self.showBoard()
        self.ready()

    def ready(self, one=None):
        self.perspective.callRemote('startGame')

    def remote_joined(self, playerName):
        self.board.addPlayer(playerName)
        self.addPlayer(playerName)

    def addPlayer(self, playerName):
        r = int(self.boardSize / (2 * self.board.maxPlayers))
        #print r
        mx = conf.WINWIDTH - (2 * r)
        my = r
        self.players.append(playerName)
        log.msg('players: %s' % self.players)
        color = COLORS[self.players.index(playerName)]
        marker = Drawable.Circle(self.window, r,
                                   color=color)
        name = Drawable.String(self.window, playerName.center(9),
                                 fontSize=int(r/2))
        stack = Drawable.StationaryStack(self.window)
        self.playerMarkers[playerName] = stack
        marker.set_position((mx, (2*r)*(len(self.players)-1) + r))
        name.set_position((mx + (r/4), (2*r)*(len(self.players)-1) + r + my))
        stack.push(marker)
        stack.push(name)

    def remote_start(self):
        self.board.startGame()
        self.start()

    def start(self):
        pass

    def remote_left(self, playerName):
        self.board.removePlayer(playerName)
        self.players.remove(playerName)
        self.removePlayer(playerName)

    def removePlayer(self, playerName):
        self.playerMarkers[playerName].empty()

    def remote_badMove(self):
        self.badMove()
        self.makeMove()

    def badMove(self):
        log.msg('errrk')

    def remote_sync(self, board):
        """This should not happen.

        XXX: If it does, this will not work anyhow.

        """

        self.board.board = board

    def remote_showMove(self, playerName, position):
        self.board.move(playerName, position)
        self.showMove(playerName, position)

    def showMove(self, playerName, position):
        x, y = position
        px0 = self.px0
        py0 = self.py0
        boxSize = int(self.boardSize / self.board.size)
        markerSize = int(boxSize / 2) - 5

        color = COLORS[self.players.index(playerName)]
        px = px0 + x*boxSize + 2
        py = py0 + y*boxSize + 2
        c = Drawable.Circle(self.window, markerSize, color=color)
        c.set_position((px, py))
        stat = Drawable.Stationary(self.window, c)
        stat.draw()
        log.msg("%s moved %s" % (playerName, position))

    def remote_go(self):
        if hasattr(self, 'msg'):
            self.msg.clear()
        goMsg = Drawable.String(self.window, 'YOUR TURN')
        goMsg.set_position((20, 5))
        self.msg = Drawable.Stationary(self.window, goMsg)
        self.msg.draw()
        self.makeMove()

    def makeMove(self):
        #log.msg('Your turn: ')
        self.myTurn = 1

    def move(self, position):
        if self.myTurn:
            self.myTurn = 0
            self.perspective.callRemote('move', position)
            self.showMove(self.name, position)
            self.msg.clear()
            del(self.msg)

    def remote_wait(self, playerName):
        if hasattr(self, 'msg'):
            self.msg.clear()
        waitMsg = Drawable.String(message='%s TURN' % playerName)
        waitMsg.set_position((20, 5))
        self.msg = Drawable.Stationary(sprite=waitMsg)
        self.msg.draw()
        self.wait(playerName)

    def wait(self, playerName):
        p = self.players.index(playerName)
        self.board.player = p
        #log.msg('%s turn' % playerName)

    def remote_gameOver(self, playerName):
        self.gameOver(playerName)

    def gameOver(self, playerName):
        log.msg('GAME OVER %s' % playerName)
        if hasattr(self, 'msg'):
            self.msg.clear()
        overMsg = Drawable.String(message='GAME OVER')
        overMsg.set_position((20, 5))
        self.msg = Drawable.Stationary(sprite=overMsg)
        self.msg.draw()
        self.whenReady()

    def positionClicked(self, pygameEvent=None):
        if pygameEvent is None:
            #print 'no event'
            return
        pos = pygameEvent.pos
        px, py = pos
        #print 'pos', pos

        size = self.board.size
        boardSize = self.boardSize
        boxSize = int(boardSize / size)

        px0 = self.px0
        py0 = self.py0
        pxMax = px0 + size*boxSize
        pyMax = py0 + size*boxSize

        if px < px0 or px > pxMax or py < py0 or py > pyMax:
            return None
        else:
            x = -1
            for xEdge in range(px0, pxMax, boxSize):
                if px > xEdge:
                    x += 1
            y = -1
            for yEdge in range(py0, pyMax, boxSize):
                if py > yEdge:
                    y += 1
            self.move((x, y))

    def initialize(self):
        self.set_background(tilename='bg9.png')
        self.boardSize = int(conf.WINHEIGHT * 0.8)
        self.px0 = self.py0 = int(conf.WINHEIGHT * 0.1)

        self.players = []
        self.myTurn = 0
        self.playerMarkers = {}
        self.set_name()
        self.connect()

        self.startedServer = 0

        self.events.add(Event.MOUSEBUTTONDOWN_Event(button=1,
                                            callback=self.positionClicked))




def main():

    w = Screen.Window()
    game = TG(w, reactor, delay=0.1)
    game.mainloop()

    reactor.run()

if __name__ == '__main__':
    main()
