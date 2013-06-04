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

"""Drawable objects which track the mouse.

"""

import pygame
import pygame.draw
#from pygame.locals import *

import Drawable
from locals import WHITE, BLACK, TRANSPARENT

class AbstractClassError(Exception):
    """
    """

    pass

class Cursor:
    """
    """
    def __init__(self, screen=None):
        self.hotspot = [0, 0]

    def set_hotspot(self, position=None):
        if position is None:
            h, w = self.image.get_size()
            hx, hy = w/2, h/2
            position = (hx, hy)
        self.hotspot[0] = position[0]
        self.hotspot[1] = position[1]

    def get_hotspot(self):
        x, y = self.get_position()
        hx, hy = self.hotspot
        return x+hx, y+hy

    def move(self):
        self.set_position(pygame.mouse.get_pos())
        pygame.event.pump()


class CircleCursor(Cursor, Drawable.Circle):
    """Circle shape"""
    
    def __init__(self, w=None, radius=10, color=WHITE):
        Cursor.__init__(self)
        Drawable.Circle.__init__(self, w, radius, color)
        self.set_hotspot()


class ImageCursor(Cursor, Drawable.Image):
    """Image loaded from file"""

    def __init__(self, w=None, filename=None):
        Cursor.__init__(self)
        Drawable.Image.__init__(self, w, filename)
        self.set_hotspot()


class MultiImageCursor(Cursor, Drawable.MultiImage):
    """Image loaded from file"""

    def __init__(self, w=None, filenames=None):
        Cursor.__init__(self)
        Drawable.MultiImage.__init__(self, w, filenames)
        self.set_hotspot()


class AnimatedCursor(Cursor, Drawable.AnimatedImage):
    """Sequence of images loaded from list of files"""

    def __init__(self, w=None, filenames=[]):
        Cursor.__init__(self)
        Drawable.AnimatedImage.__init__(self, w, filenames)
        self.set_hotspot()

    def move(self):
        Drawable.AnimatedImage.move(self)
        Cursor.move(self)


class XCursor(Cursor, Drawable.Square):
    """X shape"""
    
    def __init__(self, w=None, size=11, color=BLACK):
        Cursor.__init__(self)
        if size % 2 == 0:
            size += 1
        Drawable.Square.__init__(self, w, size, color=TRANSPARENT)
        self.image.set_colorkey(TRANSPARENT)
        pygame.draw.line(self.image, color, (0, 0), (size-1, size-1), 1)
        pygame.draw.line(self.image, color, (0, size-1), (size-1, 0), 1)

        center = int(size / 2)
        self.set_hotspot()


class CrosshairCursor(Cursor, Drawable.Square):
    """Like gun crosshairs"""
    
    def __init__(self, w=None, size=11):
        Cursor.__init__(self)
        if size < 9:
            size = 9
        if size % 2 == 0:
            size += 1
        Drawable.Square.__init__(self, w, size, color=TRANSPARENT)
        self.image.set_colorkey(TRANSPARENT)
        center = int(size / 2)
        pygame.draw.circle(self.image, BLACK, (center, center), center-3, 1)
        pairs = (((center+2, center), (size-3, center)),
                ((center-2, center), (1, center)),
                ((center, center+2), (center, size-3)),
                ((center, center-2), (center, 1)))
        for pair in pairs:
            pygame.draw.line(self.image, BLACK, pair[0], pair[1], 1)

        self.set_hotspot()
