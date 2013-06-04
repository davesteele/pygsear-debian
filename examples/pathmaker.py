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

import time, random, math

import pygame
import pygame.draw
from pygame.locals import K_RETURN

from pygsear import Game, Drawable, Event, Cursor, Widget, conf
from pygsear.locals import WHITE

class Pathmaker(Game.Game):
    def printPath(self, ev=None):
        for place in self.pathList:
            print place.get_position()

    def clearPath(self, ev=None):
        bg = self.bg
        self.pathList = []
        self.pathPlaces.clear()
        self.pathPlaces.empty()
        pygame.display.update()
        del self.oldX
        del self.oldY

    def penUp(self, ev=None):
        self.pen = 0

    def penDown(self, ev=None):
        self.pen = 1

    def set_minimumDistance(self, minimumDistance):
        self.minimumDistance = minimumDistance

    def set_maximumDistance(self, maximumDistance):
        self.maximumDistance = maximumDistance

    def checkMinimumDistance(self, place):
        x, y = place
        if not hasattr(self, 'oldX') or not hasattr(self, 'oldY'):
            self.oldX, self.oldY = x, y
            return 1
        else:
            dx = self.oldX - x
            dy = self.oldY - y
            distance = math.hypot(dx, dy)
            #print distance
            if distance > self.minimumDistance:
                self.oldX, self.oldY = x, y
                return 1
            else:
                return 0

    def restrictDistance(self, place):
        x, y = place
        if not hasattr(self, 'oldX') or not hasattr(self, 'oldY'):
            self.oldX, self.oldY = x, y
            return place
        else:
            dx = self.oldX - x
            dy = self.oldY - y
            distance = math.hypot(dx, dy)
            if distance > self.maximumDistance:
                angle = math.atan2(dy, -dx)
                dx = self.maximumDistance * math.cos(angle)
                dy = self.maximumDistance * math.sin(angle)
                x = int(self.oldX + dx)
                y = int(self.oldY - dy)
                pygame.mouse.set_pos(x, y)
                return x, y
            else:
                return place

    def initialize(self):
        self.set_background()
        self.window.set_title('PATHMAKER')
        self.clock = pygame.time.Clock()

        msg = """Note:\nThis script is not used much, and is not maintained"""
        dlg = Widget.Dialog_OK(message=msg)
        dlg.modal()

        pygame.mouse.set_visible(0)

        self.events.add(Event.MOUSEBUTTONDOWN_Event(button=1, callback=self.penDown))
        self.events.add(Event.MOUSEBUTTONUP_Event(button=1, callback=self.penUp))
        self.events.add(Event.MOUSEBUTTONDOWN_Event(button=3, callback=self.clearPath))
        self.events.add(Event.KEYUP_Event(key=K_RETURN, callback=self.printPath))

        cursor = Cursor.XCursor(self.window, 11, color=WHITE)
        self.cursor = cursor
        self.sprites.add(cursor)

        self.pathPlaces = self.addGroup()
        self.pathList = []

        self.penUp()
        self.set_minimumDistance(6)
        self.set_maximumDistance(10)


    def mainloop(self):
        while not self.quit:
            self.clock.tick(conf.MAX_FPS)
            self.checkEvents()
            self.sprites.clear()

            self.sprites.move()
            if self.pen:
                place = self.cursor.get_hotspot()
                place = self.restrictDistance(place)
                if self.checkMinimumDistance(place):
                    marker = Drawable.Square(side=4)
                    marker.set_position(place)
                    self.pathPlaces.add(marker)
                    self.pathList.append(marker)

            dirty = self.sprites.draw()
            dirty += self.pathPlaces.draw()
            self.update(dirty)


def main():

    print "press [ENTER] to print path list"

    g = Pathmaker()
    g.mainloop()

if __name__ == '__main__':
    main()
