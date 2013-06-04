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
from pygame.locals import K_ESCAPE, K_s, K_h, K_q

import pygsear
from pygsear import conf
from pygsear.Drawable import EuclidTurtle
from pygsear.locals import *

from pygsear.Game import Game
from pygsear import Event

class EPenguin(EuclidTurtle):
    def __init__(self, w=None):
        EuclidTurtle.__init__(self, w, filename='epeng.png', colorkey=None,
                                convert=0)

    def welcome(self):
        self.right(90)
        self.write('welcome to euclid')

    def squares(self, width=4, height=7):
        pen = self.pen
        self.penUp()

        for w in range(width):
            for h in range(height):
                self.square(1)
                self.forward(1)
            self.backward(height)
            self.right(90)
            self.forward(1)
            self.left(90)
        self.right(90)
        self.backward(width)
        self.left(90)

        if pen:
            self.penDown()
        else:
            self.penUp()

    def pythagoras(self):
        self.moveTo((-2, 1.5))
        self.turnTo(-90)
        self.squares(3, 3)
        self.moveTo((-2, -1.5))
        self.turnTo(0)
        self.squares(4, 4)
        self.moveTo((2, -1.5))
        self.turnTo(143.1)
        self.squares(5, 5)

    def tangent(self, radius=5, deg=30):
        self.cCircle(radius)
        
        rad = deg * (math.pi / 180)
        x = radius * math.cos(rad)
        y = radius * math.sin(rad)

        try:
            m = float(-x) / y
            if abs(m) < 0.000001:
                m = 0
        except ZeroDivisionError:
            m = 999999
            
        dirty = self.line_point_slope((x, y), m)
        self.update(dirty)

    def tangents(self):
        r = 1
        while r <= 7:
            self.tangent(r, (180 * (r / 7.0)))
            r += 0.1
            self.nudge_color(red='102%', blue='97.5%')

    def logarithm(self):
        x = 0.01
        y = math.log(x)
        self.moveTo((x, y))

        while x < 15:
            y = math.log(x)
            self.lineTo((x, y))
            x += 0.1

    def f_of_x(self, f=None):
        if f is None:
            functions = ['(x**3 / 5 - x**2 - x)',
                            '(x**2 - x - 5)',
                            '(math.sin(x) + x)']
            f = random.choice(functions)

        x = -15.0
        y = eval(f)
        self.moveTo((x, y))

        while x < 15:
            y = eval(f)
            self.lineTo((x, y))
            x += 0.1

    def writeFuncName(self, funcName):
        color = self.color
        self.set_color(WHITE)
        self.moveTo((-10, 7))
        self.turnTo(0)
        self.write(funcName+'()')
        self.home()
        self.set_color(color)

    def testfuncs(self):
        funcs = ['squares', 'pythagoras', 'tangent', 'tangents', 'logarithm', 'f_of_x']
        return funcs

class DemoEPenguin(EPenguin):
    def set_demo(self, demo):
        #print 'setting'
        self.demo = demo
        self.move = self.demomove

    def demomove(self):
        #print 'checking'
        self.demo.checkEvents()
        #print 'moving'
        EPenguin.move(self)

class SkipTest(Exception):
    pass

class EPenguinDemo(Game):
    def __init__(self):
        self._in_test = 0
        Game.__init__(self)

    def skipfunc(self, ev=None):
        raise SkipTest

    def hide(self):
        if self.tom.visible:
            self.tom.hide()
        else:
            self.tom.uclear()
            self.tom.show()
    
    def resize_reset(self):
        self.initialize()
        self.tom.center()
        self.tom.set_home()
        self.resized = 1

    def configure(self):
        self.resized = 0
        Game.configure(self)
        if self.resized:
            self.resized = 0
            if self._in_test:
                raise SkipTest

    def initialize(self):
        Game.initialize(self)
        self.tom = DemoEPenguin()
        self.tom.set_demo(self)

        self.events.add(Event.QUIT_Event(callback=self._quit))
        self.events.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self.configure))

        self.events.add(Event.KEYUP_Event(key=K_s, callback=self.skipfunc))
        self.events.add(Event.KEYUP_Event(key=K_h, callback=self.hide))
        self.events.add(Event.KEYUP_Event(key=K_q, callback=self._quit))

    def checkEvents(self):
        self.events.check()
        if self.quit:
            import sys
            sys.exit()

    def mainloop(self):
        funcs = self.tom.testfuncs()
        random.shuffle(funcs)

        funcs.insert(0, 'welcome')

        self._in_test = 1
        for func in funcs:
            try:
                self.tom.clearScreen()
                self.tom.euclidean()
                self.tom.home()
                self.tom.penDown()

                self.tom.set_color('random')

                self.tom.writeFuncName(func)

                f = getattr(self.tom, func)
                f()
                
                self.tom.writeFuncName(func)

                self.checkEvents()

                self.waitFor(timeout=2500)

                if self.quit:
                    break

            except SkipTest:
                self.tom.rollback_fill()
                self.tom.rollback()


if __name__ == '__main__':
    demo = EPenguinDemo()
    demo.mainloop()

else:
    # do this, just to show the splash screen
    Game()

    print """

pygsear euclid graphics

Type help for a brief introduction

"""

    from site import _Helper
    class Help(_Helper):
        def __repr__(self):
            return """
Welcome to pygsear's euclid graphics module.

You can make the graphic window smaller by typing:
shrink()

To move the penguin try forward, backward, left, and right, ie:
forward(5)
right(45)
backward(3)
left(90)

You can, of course put a different number inside of
the parenthesis. Other commands include circle, cCircle,
square, cSquare, and many demonstration functions.

To see a complete list, type:
dir(tom)

most of those functions will need to be accessed through the
penguin, ie tom.squares()  or tom.pythagoras() but some have
been pulled in to the local scope. To see local functions try:
dir()
            
            """


    tom = EPenguin()

    forward = tom.forward
    backward = tom.backward
    right = tom.right
    left = tom.left
    home = tom.home
    reset = tom.reset
    refresh = tom.refresh
    clearScreen = tom.clearScreen
    cls = clearScreen
    write = tom.write
    circle = tom.circle
    cCircle = tom.cCircle
    turnTo = tom.turnTo
    penUp = tom.penUp
    penDown = tom.penDown
    set_color = tom.set_color
    shrink = tom.shrink
