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


import copy

import pygame
from pygame.locals import K_RETURN, K_a, K_s, K_x, K_z, K_UP, K_DOWN

from pygsear.Drawable import Square, Layer
from pygsear.Game import Game
from pygsear.Event import MOUSEBUTTONDOWN_Event, MOUSEBUTTONUP_Event, KEYUP_Event
from pygsear.locals import WHITE, BLACK, COLORS, BLUE, RED, GREEN, ORANGE, YELLOW, TRANSPARENT, LGREEN, LBLUE


class BGame(Game):
    def initialize(self):
        s = Bezier()
        s.center()
        self.s = s

        self.sprites.add(s)

        self.events.add(MOUSEBUTTONDOWN_Event(callback=s.mouseClicked))
        self.events.add(MOUSEBUTTONUP_Event(callback=s.mouseReleased))

        self.events.add(KEYUP_Event(key=K_RETURN, callback=s.report))

        self.events.add(KEYUP_Event(key=K_a, callback=s.add_point_front))
        self.events.add(KEYUP_Event(key=K_s, callback=s.add_point_end))
        self.events.add(KEYUP_Event(key=K_x, callback=s.remove_point))

        self.events.add(KEYUP_Event(key=K_z, callback=s.toggle_fun_display))

        self.events.add(KEYUP_Event(key=K_UP, callback=s.add_report_point))
        self.events.add(KEYUP_Event(key=K_DOWN, callback=s.remove_report_point))

    def checkEvents(self):
        Game.checkEvents(self)
        self.s.move_point()


class Bezier(Layer):
    def __init__(self, points=None):
        Layer.__init__(self)
        self.image.set_colorkey(TRANSPARENT)

        w, h = self.image.get_size()
        self.w = w
        self.h = h

        self.selected = 0
        self.button_held = 0
        self.display_fun = 1
        self.n_report = 10

        if points is None:
            points = [[30, 53], [265, 571], [462, 445], [695, 56], [781, 572]]
        self.points = points

        self.drawSpline()
        self.drawFun()

    def report(self, ev):
        step = int(len(self.spline) / self.n_report)
        points = self.spline[::step]
        points.append(self.spline[-1])
        print [(int(x), int(y)) for x, y in points]
        self.show_report_points()

    def add_report_point(self, ev):
        self.n_report += 1
        self.drawSpline()
        self.show_report_points()

    def remove_report_point(self, ev):
        self.n_report -= 1
        self.drawSpline()
        self.show_report_points()

    def show_report_points(self):
        step = int(len(self.spline) / self.n_report)
        points = self.spline[::step]
        points.append(self.spline[-1])
        for p in points:
            pygame.draw.rect(self.image, WHITE, (p, (3, 3)))

    def add_point_front(self, ev):
        self.points.insert(0, [250, 250])
        self.drawSpline()
        self.drawFun()

    def add_point_end(self, ev):
        self.points.append([250, 250])
        self.drawSpline()
        self.drawFun()

    def remove_point(self, ev):
        if len(self.points) > 1:
            try:
                self.points.pop(self.selected)
            except IndexError:
                try:
                    self.points.pop()
                except IndexError:
                    pass
            self.drawSpline()
            self.drawFun()

    def toggle_fun_display(self, ev):
        self.display_fun = not self.display_fun
        self.drawFun()

    def mouseClicked(self, ev):
        self.button_held = 1

        x, y = pygame.mouse.get_pos()

        selected = None
        rmin = 1000000

        for point in self.points:
            px, py = point
            dx, dy = x-px, y-py
            r = dx*dx + dy*dy
            if r < rmin:
                selected = point
                rmin = r

        self.selected = self.points.index(selected)

    def mouseReleased(self, ev):
        self.button_held = 0

    def move_point(self):
        if self.button_held:
            self.points[self.selected][:] = list(pygame.mouse.get_pos())
            self.drawSpline()

    def drawSpline(self):
        self.image.fill(TRANSPARENT)
        self.spline = []

        # Draw the points
        for p in self.points:
            pygame.draw.rect(self.image, BLUE, (p, (3, 3)))

        # Draw the control lines
        if len(self.points) > 2:
            pygame.draw.lines(self.image, GREEN, False, self.points)

        # Draw the curve
        step = 1.0 / self.w
        t = step

        pold = self.points[0]
        for k in range(self.w):
            pi = copy.deepcopy(self.points)
            for j in range(len(self.points)-1, 0, -1):
                for i in range(j):
                    pi[i][0] = (1-t)*pi[i][0] + t*pi[i+1][0]
                    pi[i][1] = (1-t)*pi[i][1] + t*pi[i+1][1]

            p = pi[0]
            self.spline.append(p)
            pygame.draw.line(self.image, RED, pold, p)
            pold = p

            t += step

    def drawFun(self):
        self.window.bg.fill(BLACK)

        if self.display_fun:
            step = 1.0 / self.w
            t = step

            n = len(self.points)

            B = [0 for x in range(n)]
            Bold = copy.copy(B)
            B[0] = self.h

            for k in range(self.w):
                Bold = copy.copy(B)

                for j in range(n):
                    for i in range(j, 0, -1):
                        B[i] = (1-t)*B[i] + t*B[i-1]

                for m in range(n):
                    color = [RED, GREEN, ORANGE, BLUE, WHITE, YELLOW, LGREEN, LBLUE][m % 8]
                    p1 = (k, Bold[m])
                    p2 = (k, B[m])
                    pygame.draw.line(self.window.bg, color, p1, p2)

                t += step


if __name__ == '__main__':
    g = BGame()
    g.mainloop()

