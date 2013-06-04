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

"""Interfaces with the Pygame display"""

import time, random, math
import os

import pygame
import pygame.draw
from pygame.locals import FULLSCREEN

import conf
from Util import load_image
from locals import WHITE, BLACK

class Layer:
    """Holds foreground and background pygame surfaces"""

    def __init__(self, size=None):
        if size is None:
            size = conf.WINSIZE
        self.size = size
        self._fg = pygame.Surface(size)
        self._bg = pygame.Surface(size)
        self.rect = self._fg.get_rect()
        self.offset = [0, 0]

    def clear(self):
        """Clear the screen.

        Makes the foreground surface match the background.

        """


        self._fg.blit(self._bg, (0, 0))

    def set_background(self, filename=None, img=None, tilename=None, tile=None, color=None):
        """Set the background.

        Must include just one of the keyword args:
            - C{set_background(filename)} (filename is a string)
                full size background image, should fill the screen
            - C{set_background(img)} (img is a pygame Surface)
                full size background image, should fill the screen
            - C{set_background(tilename)} (filename is a string)
                image tile will fill screen automatically
            - C{set_background(tile)} (tile is a pygame Surface)
                image tile will fill screen automatically
            - C{set_background(color=(R, G, B))}
                background will be filled with color (an RGB tuple)

        @param filename: Name of the full-screen background image.
        @param img: Full-screen background image. (pygame Surface)
        @param tilename: Name of tile image.
        @param tile: Tile image. (pygame Surface)
        @param color: Solid background color.

        """

        size = self.size

        if filename is not None:
            bg = load_image(filename)
        elif img is not None:
            bg = img
        elif tilename is not None or tile is not None:
            if tilename:
                tile = load_image(tilename)
            bg = pygame.Surface(size).convert()
            for y in range(0, size[1], tile.get_height()):
                for x in range(0, size[0], tile.get_width()):
                    bg.blit(tile, (x, y))
        else:
            if color is None:
                color = BLACK
            bg = pygame.Surface(size).convert()
            bg.fill(color)

        if hasattr(self, '_bg'):
            self._bg.blit(bg, (0, 0))
        else:
            self._bg = bg

        Layer.clear(self)

    def border(self, width=10, color=WHITE,
                    left=None, right=None, top=None, bottom=None):
        """Draw a border around the screen

        Each border width can be specified separately, or if not specified,
        will default to using width. Specify width of 0 for no border on
        a particular side.

        @param color: Color of border.

        @param width: Pixel width of border.
            If only width is passed, an equal width border will be
            drawn around the entire screen.
        
        @param left: Left-side border width.
        @param right: Right-side border width.
        @param top: Top-side border width.
        @param bottom: Bottom-side border width

        """

        bg = self._bg
        
        w, h = bg.get_size()
        
        if left is None:
            left = width
        if right is None:
            right = width
        if top is None:
            top = width
        if bottom is None:
            bottom = width

        if left:
            pygame.draw.rect(bg, color, (0, 0, left, h))
        if right:
            pygame.draw.rect(bg, color, (w-right, 0, w, h))
        if top:
            pygame.draw.rect(bg, color, (0, 0, w, top))
        if bottom:
            pygame.draw.rect(bg, color, (0, h-bottom, w, h))
        
        Layer.clear(self)

  
class Window(Layer):
    """This class interfaces with the Pygame display. By initiating
    this class, the pygame display in initiated.

    """

    def __init__(self, size=None, full=None):
        """Initialize the display window.

        @param size: 2-tuple C{(x, y)} specifies the dimensions of window.
        @param full: if True, window is fullscreen (so it's not really a window ;).

        """

        pygame.init()
        if size is None:
            size = conf.WINSIZE
        if full is not None:
            conf.WINFULL = full
        if not conf.WINFULL:
            self.screen = pygame.display.set_mode(size)
            #self.screen = pygame.display.set_mode(size, RESIZABLE)
        else:
            self.screen = pygame.display.set_mode(size, FULLSCREEN)
        Layer.__init__(self, size)
        self._fg = self.screen
        self.set_background()
        self.set_title()
        conf.window = self

    def resize(self, size):
        """Resize the window.

        Changes the pygame display mode.

        """

        w, h = size
        w = max(w, conf.MIN_WINWIDTH)
        w = min(w, conf.MAX_WINWIDTH)
        h = max(h, conf.MIN_WINHEIGHT)
        h = min(h, conf.MAX_WINHEIGHT)
        conf.WINWIDTH = w
        conf.WINHEIGHT = h
        size = (w, h)
        conf.WINSIZE = size
        self.size = size
        if not conf.WINFULL:
            self.screen = pygame.display.set_mode((w, h))
        else:
            self.screen = pygame.display.set_mode((w, h), FULLSCREEN)
        self._fg = self.screen
        self._bg = pygame.Surface((w, h))
        self.set_background()
        self.rect = self._fg.get_rect()
        conf.window = self

    def set_title(self, title='pygsear'):
        """Change the window title

        """

        pygame.display.set_caption(title)

    def update(self, areas=None):
        """Update the pygame display

        This call will update a section (or sections) of the display screen.
        You must update an area of your display when you change its contents.
        If passed with no arguments, this will update the entire display
        surface. If you have many rects that need updating, it is best to
        combine them into a sequence and pass them all at once. This call will
        accept a sequence of rectstyle arguments. Any None's in the list will
        be ignored.

        @param areas: sequence of rects to update, or if C{None} (or no
            argument is passed) will update the entire screen.

        """

        if areas is None:
            pygame.display.update()
        else:
            pygame.display.update(areas)

    def clear(self):
        """Clear the screen.

        Makes the foreground surface match the background.

        """

        Layer.clear(self)
        pygame.display.update()

    def set_background(self, filename=None, img=None, tilename=None, tile=None, color=None):
        """Set the background image"""

        Layer.set_background(self, filename, img, tilename, tile, color)
        self.bg = self._bg
        self.clear()

    def border(self, width=10, color=WHITE,
                    left=None, right=None, top=None, bottom=None):
        """Draw a border around the screen"""

        Layer.border(self, width, color, left, right, top, bottom)
        self.update()
