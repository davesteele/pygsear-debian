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

import pygame

import pygsear
from pygsear.Game import Game
from pygsear import conf

from penguin_demos import Penguin, PenguinDemo


if __name__ == '__main__':
    demo = PenguinDemo()
    demo.mainloop()

else:
    # do this, just to show the splash screen
    Game()

    print """

pygsear penguin graphics

Type help for a brief introduction

"""

    from site import _Helper
    class Help(_Helper):
        def __repr__(self):
            return """
Welcome to pygsear's penguin graphics module.

You can make the graphic window smaller by typing:
shrink()

To move the penguin try forward, backward, left, and right, ie:
forward(100)
right(45)
backward(75)
left(90)

You can, of course, put a different number inside of
the parenthesis. Other commands include circle, cCircle,
square, cSquare, and many demonstration functions.

To see a complete list, type:
dir(pete)

most of those functions will need to be accessed through the
penguin, ie pete.star()  or pete.starryNight() but some have
been pulled in to the local scope. To see local functions try:
dir()
            
            """

    # create the turtle
    pete = Penguin()
    #pami = Penguin()

    help = Help()

    # Pull some things in to module (global) namespace
    forward = pete.forward
    backward = pete.backward
    right = pete.right
    left = pete.left

    home = pete.home
    reset = pete.reset
    refresh = pete.refresh
    clearScreen = pete.clearScreen
    cls = clearScreen

    write = pete.write
    circle = pete.circle
    cCircle = pete.cCircle
    turnTo = pete.turnTo

    penUp = pete.penUp
    penDown = pete.penDown
    set_color = pete.set_color

    shrink = pete.shrink
    grow = pete.grow

    begin = pete.begin
    commit = pete.commit
    rollback = pete.rollback


try:
    import threading

    class PWorker(threading.Thread):
        def __init__(self, pygame):
            self.pygame = pygame
            self.done = 0
            threading.Thread.__init__(self)

        def run(self):
            while not self.done:
                self.pygame.display.update()
                time.sleep(1)

        def stop(self):
            self.done = 1

    if not hasattr(conf, 'BG_THREAD_STARTED'):
        pw = PWorker(pygame)
        pw.start()

        def killpw():
            pw.stop()

        import atexit
        atexit.register(killpw)

        conf.BG_THREAD_STARTED = 1

except ImportError:
    print "No threading available"
    print "use refresh() to repaint the screen"
