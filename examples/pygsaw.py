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

import time, random, math, sys

import pygame
import pygame.draw
from pygame.locals import *

from pygsear import conf
pygame.display.init()
modes = pygame.display.list_modes()
modes.sort()
modes.reverse()
w, h = modes[0]

conf.WINWIDTH = w
conf.WINHEIGHT = h
conf.WINSIZE=(conf.WINWIDTH, conf.WINHEIGHT)
conf.WINFULL= 1

from pygsear import Screen, Game, Drawable
from pygsear.Util import load_image
from pygsear.locals import TRANSPARENT2, RED, BLACK

BORDER = 100

class Piece(Drawable.MultiImage):
    def __init__(self, window, image):
        Drawable.MultiImage.__init__(self, window)
        self.addImage(filename='default', image=image, colorkey=TRANSPARENT2)
        self.flip()
        self.edge = 0
        self.chunk = Chunk(self)

    def set_offset(self, pos, chunked=0):
        if self.chunk is None or chunked:
            cursorx, cursory = pos
            x, y = self.get_position()
            self.offset = (x - cursorx, y - cursory)
        else:
            self.chunk.set_offset(pos)

    def drag(self, pos, chunked=0):
        if self.chunk is None or chunked:
            x, y = pos
            offx, offy = self.offset
            x += offx
            y += offy
            self.set_position((x, y))
        else:
            self.chunk.drag(pos)

    def connect(self):
        x, y = self.get_position()
        w, h = self.image.get_size()
        e = self.edgeWidth
        grab = self.grabWidth
        for k in self.neighbors.keys():
            grabOk = 0
            piece = self.neighbors[k]
            if piece is not None and self.rect.colliderect(piece.rect):
                px, py = piece.get_position()
                grabOk = 0
                if k == 'above':
                    if 0 < py + h - y < 2 * grab and \
                        -grab < x - px < grab:
                        dx = x - px
                        dy = y - h + e + e - py
                        piece.chunk.nudge(dx, dy)
                        piece.chunk.reChunk(self.chunk)

                elif k == 'below':
                    if -2 * grab < py - y - h < 0 and \
                        -grab < x - px < grab:
                        dx = x - px
                        dy = y + h - e - e - py
                        piece.chunk.nudge(dx, dy)
                        piece.chunk.reChunk(self.chunk)

                elif k == 'left':
                    if -2 * grab < x - px - w < 0 and \
                        -grab < y - py < grab:
                        dx = x - w + e + e - px
                        dy = y - py
                        piece.chunk.nudge(dx, dy)
                        piece.chunk.reChunk(self.chunk)

                elif k == 'right':
                    if 0 < x - px + w < 2 * grab and \
                        -grab < y - py < grab:
                        dx = x + w - e - e - px
                        dy = y - py
                        piece.chunk.nudge(dx, dy)
                        piece.chunk.reChunk(self.chunk)


    def jigsawEdges(self):
        neighbors = self.neighbors
        edgeWidth = self.edgeWidth
        piece_w = self.piece_w
        piece_h = self.piece_h

        colorkey = self.image.get_colorkey()
        self.image.set_colorkey()
        if neighbors.has_key('below') and neighbors['below']:
            neighbor = neighbors['below']
            image = self.image
            neighbor_image = neighbor.image
            if random.randint(0, 1):
                flipy = 1
                image, neighbor_image = neighbor_image, image
                image = pygame.transform.flip(image, 0, 1)
                neighbor_image = pygame.transform.flip(neighbor_image, 0, 1)
            else:
                flipy = 0
            cutout_w = random.randint(int(2*piece_w/10), int(8*piece_w/10))
            cutout_h = random.randint(int(2*edgeWidth/5), int(4*edgeWidth/5))
            cutout_x = int((piece_w - cutout_w) / 2) + edgeWidth
            cutout = pygame.Surface((cutout_w, cutout_h))
            cutout.blit(neighbor_image,
                            (0, 0),
                            (cutout_x, edgeWidth, cutout_w, cutout_h))
            neighbor_image.fill(TRANSPARENT2,
                            (cutout_x, edgeWidth, cutout_w, cutout_h))
            image.blit(cutout, (cutout_x, edgeWidth+piece_h))
            if flipy:
                neighbor.image = pygame.transform.flip(image, 0, 1)
                self.image = pygame.transform.flip(neighbor_image, 0, 1)

        if neighbors.has_key('right') and neighbors['right']:
            neighbor = neighbors['right']
            image = self.image
            neighbor_image = neighbor.image
            if random.randint(0, 1):
                flipx = 1
                image, neighbor_image = neighbor_image, image
                image = pygame.transform.flip(image, 1, 0)
                neighbor_image = pygame.transform.flip(neighbor_image, 1, 0)
            else:
                flipx = 0
            cutout_w = random.randint(int(2*edgeWidth/5), int(4*edgeWidth/5))
            cutout_h = random.randint(int(2*piece_h/10), int(8*piece_h/10))
            cutout_y = int((piece_h - cutout_h) / 2) + edgeWidth
            cutout = pygame.Surface((cutout_w, cutout_h))
            cutout.blit(neighbor_image,
                            (0, 0),
                            (edgeWidth, cutout_y, cutout_w, cutout_h))
            neighbor_image.fill(TRANSPARENT2,
                            (edgeWidth, cutout_y, cutout_w, cutout_h))
            image.blit(cutout, (edgeWidth+piece_w, cutout_y))
            if flipx:
                neighbor.image = pygame.transform.flip(image, 1, 0)
                self.image = pygame.transform.flip(neighbor_image, 1, 0)
        self.image.set_colorkey(colorkey)


class Chunk:
    def __init__(self, piece):
        piece.chunk = self
        self.pieces = {piece: 0}

    def reChunk(self, chunk):
        for piece in self.pieces:
            piece.chunk = chunk
            chunk.pieces[piece] = 0

    def nudge(self, dx, dy):
        for piece in self.pieces:
            x, y = piece.get_position()
            piece.set_position((x+dx, y+dy))

    def set_offset(self, pos):
        for piece in self.pieces:
            piece.set_offset(pos, chunked=1)

    def drag(self, pos):
        for piece in self.pieces:
            piece.drag(pos, chunked=1)

class Puzzle:
    """The jigsaw puzzle picture and all of its pieces"""

    def __init__(self, window, image):
        self.window = window
        self.image = image
        self.normalize()

    def normalize(self):
        w, h = self.image.get_size()
        ratio = float(w) / h
        screen_ratio = float(conf.WINWIDTH - 2 * BORDER)/(conf.WINHEIGHT - 2 * BORDER)

        if ratio >= screen_ratio:
            new_w = conf.WINWIDTH - (2 * BORDER)
            new_h = float(new_w) / ratio
        else:
            new_h = conf.WINHEIGHT - (2 * BORDER)
            new_w = new_h * ratio

        scale = float(new_h) / h
        self.image = pygame.transform.rotozoom(self.image, 0, scale)

    def show(self):
        self.window.screen.blit(self.image, (BORDER, BORDER))
        pygame.display.flip()

    def showPieces(self):
        pieces = self.pieces
        for x in range(len(pieces)):
            for piece in pieces[x]:
                piece.set_position((random.randint(0, conf.WINWIDTH-BORDER),
                                    random.randint(0, conf.WINHEIGHT-BORDER)))
                piece.draw()
        self.window.update()

    def shuffle(self):
        pieces = self.pieces
        for x in range(len(pieces)):
            for piece in pieces[x]:
                piece.set_position((random.randint(0, conf.WINWIDTH-BORDER),
                                    random.randint(0, conf.WINHEIGHT-BORDER)))

    def cut(self, nw, nh, edgeWidth=20, mark_edges=0):
        w, h = self.image.get_size()
        self.nw = nw
        self.nh = nh
        piece_w = int(w / nw)
        piece_h = int(h / nh)

        surf_w = piece_w + edgeWidth + edgeWidth
        surf_h = piece_h + edgeWidth + edgeWidth

        pieces = []
        stack = []
        edges = []
        e = edgeWidth - 1
        for x in range(nw):
            pieces.append([])
            for y in range(nh):
                image = pygame.Surface((surf_w, surf_h))
                image.fill(TRANSPARENT2)
                #image.fill(BLUE)
                image.blit(self.image, (edgeWidth, edgeWidth),
                            ((x * piece_w), (y * piece_h),
                                piece_w, piece_h))
                piece = Piece(self.window, image)
                piece.piece_w = piece_w
                piece.piece_h = piece_h
                piece.edgeWidth = edgeWidth
                piece.grabWidth = edgeWidth
                if x == 0 or x == nw-1 or y == 0 or y == nh-1:
                    piece.edge = 1
                    edges.append(piece)
                    if mark_edges:
                        if x == 0:
                            pygame.draw.line(image, RED,
                                        (e-1, e),
                                        (e-1, piece_h+e), 3)
                        elif x == nw-1:
                            pygame.draw.line(image, RED,
                                        (piece_w+edgeWidth, e),
                                        (piece_w+edgeWidth,
                                            piece_h+e), 3)
                        if y == 0:
                            pygame.draw.line(image, RED,
                                        (e, e),
                                        (piece_w+e, e), 3)
                        elif y == nh-1:
                            pygame.draw.line(image, RED,
                                        (e, piece_h+edgeWidth),
                                        (piece_w+e,
                                            piece_h+edgeWidth), 3)

                pieces[x].append(piece)
                stack.append(piece)

        self.pieces = pieces
        self.stack = stack
        self.edges = edges

    def set_neighbors(self):
        pieces = self.pieces
        for x in range(self.nw):
            for y in range(self.nh):
                piece = pieces[x][y]

                neighbors = {}
                if y > 0:
                    neighbors['above'] = pieces[x][y-1]
                else:
                    neighbors['above'] = None

                if x > 0:
                    neighbors['left'] = pieces[x-1][y]
                else:
                    neighbors['left'] = None

                if x < self.nw-1:
                    neighbors['right'] = pieces[x+1][y]
                else:
                    neighbors['right'] = None

                if y < self.nh-1:
                    neighbors['below'] = pieces[x][y+1]
                else:
                    neighbors['below'] = None

                piece.neighbors = neighbors

    def joinEdges(self):
        pieces = self.pieces
        for x in range(self.nw):
            for y in range(self.nh):
                piece = pieces[x][y]
                piece.jigsawEdges()


class PuzzleGame(Game.Game):
    def __init__(self, window, puzzle):
        self.puzzle = puzzle
        window.set_title('Pygsaw')
        Game.Game.__init__(self, window)
        pygame.event.set_allowed([KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    def checkEvents(self):
        for e in pygame.event.get():
            if e.type == QUIT:
                self.quit = 1
                break
            elif e.type == KEYUP and e.key == K_ESCAPE:
                self.quit = 1
                break
            elif e.type == MOUSEBUTTONDOWN:
                rev = self.puzzle.stack[:]
                rev.reverse()
                if e.button == 1:
                    for piece in rev:
                        if piece.rect.collidepoint(e.pos):
                            self.puzzle.stack.remove(piece)
                            self.puzzle.stack.append(piece)
                            self.dragging = piece
                            piece.set_offset(e.pos)
                            break
                elif e.button == 3:
                    for piece in self.puzzle.stack:
                        if piece.rect.collidepoint(e.pos):
                            self.puzzle.stack.remove(piece)
                            self.puzzle.stack.insert(0, piece)

            elif e.type == MOUSEBUTTONUP:
                if self.dragging is not None:
                    self.dragging.connect()
                self.dragging = None

    def initialize(self):
        self.set_background(color=(75, 105, 75))

        msg = Drawable.String(message="Press [ESC] to quit", fontSize=30, color=BLACK)
        msg.set_position(10, conf.WINHEIGHT-30)
        msg = Drawable.Stationary(sprite=msg)
        msg.draw()

        self.clock = pygame.time.Clock()

        pygame.event.set_blocked(MOUSEMOTION)

        self.dragging = None
        #self.sprites.add(self.puzzle.stack)

    def mainloop(self):
        while not self.quit:
            dirty = []
            for piece in self.puzzle.stack:
                dirty.append(piece.clear())
            self.checkEvents()
            if self.dragging is not None:
                pos = pygame.mouse.get_pos()
                pygame.event.pump()
                self.dragging.drag(pos)
            for piece in self.puzzle.stack:
                dirty.append(piece.draw())
            pygame.display.update(dirty)

def main():
    pygame.display.init()

    w = Screen.Window()

    if len(sys.argv) < 2:
        imageFile = 'pygsaw_penguin.png'
    else:
        imageFile = sys.argv[1]

    i = load_image(imageFile)



    p = Puzzle(w, i)

    p.cut(6, 6, mark_edges=1)
    p.set_neighbors()
    p.joinEdges()
    p.shuffle()

    g = PuzzleGame(w, p)
    g.mainloop()

if __name__ == '__main__':
    main()
