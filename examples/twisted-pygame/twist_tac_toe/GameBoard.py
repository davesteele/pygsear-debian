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
import random

from twisted.python import log

class GameBoardError:
    pass

class GameBoard:
    def __init__(self, size=3, toWin=3, maxPlayers=2):
        self.set_size(size)
        self.set_toWin(toWin)
        self.set_maxPlayers(maxPlayers)
        self.reset_board()
        self.reset_game()

    def reset_board(self):
        log.msg('resetting Board')
        self.board = {}
        self.started = 0
        self.over = 0

    def reset_game(self):
        self.players = []
        self.player = 0
        self.queue = []

    def startGame(self):
        if not self.started and len(self.players) > 1:
            self.started = 1
        else:
            log.msg('started %s, players %s' % (self.started, self.players))
            raise GameBoardError

    def get_board(self):
        return self.board

    def set_size(self, size=3):
        self.size = size

    def set_toWin(self, toWin=3):
        self.toWin = toWin

    def set_maxPlayers(self, maxPlayers=2):
        self.maxPlayers = maxPlayers

    def showBoard(self):
        out = ''
        for row in range(self.size):
            for col in range(self.size):
                if self.board.has_key((col, row)):
                    out += '%s' % self.board[(col, row)]
                else:
                    out += '+'
            out += '\n'
        print out

    def addPlayer(self, player):
        if len(self.players) < self.maxPlayers:
            if player not in self.players:
                self.players.append(player)
                log.msg('adding... players now: %s' % self.players)
            else:
                log.msg('player %s already in game' % player)
        else:
            raise IndexError, "too many players"

    def removePlayer(self, player):
        self.players.remove(player)
        if self.started:
            self.over = 1

    def moveOK(self, player, position):
        #log.msg('moveOK? %s %s' % (player, self.get_nextPlayer()))
        if player != self.get_nextPlayer():
            raise ValueError, "Not your turn!"
        else:
            if position not in self.board:
                return 1
            else:
                return 0

    def move(self, player, position):
        if self.moveOK(player, position):
            self.board[position] = player
            self.checkMove(position)
            self.player += 1
            self.player = self.player % len(self.players)
        else:
            raise ValueError, "Position already occupied"

    def get_nextPlayer(self):
        return self.players[self.player]

    def checkGameOver(self):
        """True if game is over, otherwise false.

        Return the winning player, or
        if the GameBoard is full, but no winner, return 1,
        else return 0

        """

        if self.over:
            return self.over
        elif len(self.board) == self.size ** 2:
            self.over = 1
            return 1
        else:
            return 0

    def checkMove(self, position):
        """Check if position is a winning move."""

        size = self.size
        x, y = position
        match = self.board[position]
        toWin = self.toWin

        directions = {(1, 0): 'horizontal',
                        (1, 1): 'diagonalDown',
                        (0, 1): 'vertical',
                        (-1, 1): 'diagonalUp',
                        (-1, 0): 'horizontal',
                        (-1, -1): 'diagonalDown',
                        (0, -1): 'vertical',
                        (1, -1): 'diagonalUp'}
        patterns = {'horizontal': 1,
                        'vertical': 1,
                        'diagonalUp': 1,
                        'diagonalDown': 1}

        for (dx, dy), pattern in directions.items():
            px, py = position
            while 1:
                px = px + dx
                py = py + dy
                if (px, py) in self.board and self.board[(px, py)] == match:
                    patterns[pattern] += 1
                else:
                    break

        for pattern, length in patterns.items():
            if length >= toWin:
                self.over = match
                return match

def test():
    try:
        size = int(sys.argv[1])
        toWin = int(sys.argv[2])
    except:
        size = 6
        toWin = 6

    players = ['X', 'O', 'Z', 'P']

    b = GameBoard(size, toWin, len(players))

    for player in players:
        b.addPlayer(player)

    b.startGame()

    move = None
    while not b.over:
        p = b.get_nextPlayer()
        while 1:
            try:
                x = random.randrange(0, size)
                y = random.randrange(0, size)
                b.move(p, (x, y))
                break
            except ValueError:
                pass
        #print p, ' moved ', (x, y)
        b.showBoard()
        over = b.checkGameOver()
        if over == p:
            print p, ' Wins!'
        elif over:
            print 'tie game'


if __name__ == '__main__':
    test()

