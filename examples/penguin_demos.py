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
from pygame.locals import K_ESCAPE, K_s, K_h, K_q

from pygsear import conf
from pygsear.Drawable import Turtle
from pygsear.locals import *

from pygsear.Game import Game
from pygsear import Event


class Penguin(Turtle):
    COLOR = WHITE
    BGCOLOR = (75, 75, 100)

    def __init__(self, w=None):
        Turtle.__init__(self, w=w, filename='penguin_top.png', colorkey=None, convert=0)

    def welcome(self):
        self.turnTo(0)
        for place in range(20):
            self.moveTo('random')
            self.write('pygsear', fontSize=20)
        self.set_color(LGREEN)

        self.home()
        self.penUp()

        self.turnTo(180)
        self.forward(280)
        self.right(90)
        self.forward(150)
        self.right(90)
        self.rectangle(300, 275, width=0)

        self.right(90)
        self.forward(50)
        self.left(90)
        self.set_color(BLACK)
        self.write('Welcome', fontSize=60)

        self.right(90)
        self.forward(100)
        self.left(90)
        self.write('to', fontSize=40)

        self.right(90)
        self.forward(100)
        self.left(90)
        self.write('pygsear', fontSize=100)

        self.home()

        self.turnTo(0)
        self.forward(30)
        self.left(90)
        self.forward(60)
        self.right(90)
        self.set_color(BLACK)
        self.write('[ESC] to configure', fontSize=40, bgColor=LBLUE)

        self.right(90)
        self.forward(50)
        self.left(90)
        self.write('[Q] to Quit', fontSize=40, bgColor=LBLUE)

        self.right(90)
        self.forward(50)
        self.left(90)
        self.write('[S] to Skip', fontSize=40, bgColor=LBLUE)

        self.right(90)
        self.forward(50)
        self.left(90)
        self.write('[H] to sHow/Hide', fontSize=40, bgColor=LBLUE)

    def cCircles(self, r1=100, r2=20, n=60, connect=0):
        for c in range(n):
            pen = self.pen
            if not connect:
                self.penUp()
            self.forward(r1)
            self.circle(r2)
            self.forward(-r1)
            self.right(360/n)
            if pen:
                self.penDown()

    def rCircles(self, n=100, width=0, color=None):
        if color is not None:
            self.set_color(color)
        while n:
            x = random.randint(10, conf.WINWIDTH-10)
            y = random.randint(10, conf.WINHEIGHT-10)
            self.moveTo((x, y))
            if color == 'random':
                self.set_color('random')
            r = random.randint(5, 45)
            self.circle(r, width=width)
            n -= 1

    def spiral(self, turns=1, rPerT=100, stepsPerT=60, connect=0):
        center = self.get_position()
        for c in range(turns * stepsPerT):
            f = (PIx2 * rPerT/stepsPerT) * (float(c) / stepsPerT)
            self.forward(f)
            self.right(360.0 / stepsPerT)
            if connect:
                p = self.get_position()
                self.lineTo(center)
                self.lineTo(p)

    def cSpiral(self, turns=4, rPerT=80, stepsPerT=60, connect=0, rc=20,
                    color=None, width=None):
        if color is not None:
            self.set_color(color)
        pen = self.pen
        if not connect:
            self.penUp()
        for c in range(turns * stepsPerT):
            f = (PIx2 * rPerT/stepsPerT) * (float(c) / stepsPerT)
            self.forward(f)
            self.right(360.0 / stepsPerT)
            if color == 'random':
                self.set_color('random')
            self.circle(rc, width=width)
        if pen:
            self.penDown()

    def rcSpiral(self):
        turns = random.randrange(4, 24)
        rPerT = random.randrange(20, 120)
        stepsPerT = random.randrange(20, 120)
        rc = random.randrange(5, 50)
        self.cSpiral(turns, rPerT, stepsPerT, 0, rc)

    def rStar(self, n=100, color=None):
        if color is not None:
            self.set_color(color)
        x0, y0 = self.get_position()
        while n:
            x = random.randint(0, conf.WINWIDTH)
            y = random.randint(0, conf.WINHEIGHT)

            if color == 'random':
                self.set_color('random')
            dirty = self.line((x0, y0), (x, y))
            self.window.update(dirty)

            n -= 1

        if self.visible:
            self.udraw()

    def trouble(self):
        for a in range(0, 360, 12):
            self.home()
            self.turnTo(a)
            self.spiral()
        self.home()

    def poly(self, n=3, side=50):
        for s in range(n):
            self.forward(side)
            self.right(360.0 / n)

    def swirl(self, a=91, n=800, s0=1, sStep=1):
        s = s0
        while s < n:
          self.forward(s)
          self.right(a)
          s += sStep

    def lightning(self, depth=4, branches=5, length=200, color=None):
        if depth == 0:
            return
        if color is not None:
            self.set_color(color)
        p = self.get_position()
        d = self.path.get_deg()
        turn = random.randint(-30, 30)
        self.right(turn)
        f = random.randint(0, length)
        self.forward(f)
        for b in range(branches):
            self.lightning(depth-1, branches, f, color)
        self.moveTo(p)
        self.turnTo(d)

    def storm(self, color=None):
        for x in range(50, conf.WINWIDTH-50, 150):
            self.moveTo((x, 0))
            self.turnTo(270)
            self.lightning(color=color)
            self.lightning(color=color)

    def tree(self, color=None):
        self.moveTo((conf.WINWIDTH/2, conf.WINHEIGHT))
        self.turnTo(90)
        self.lightning(color=color)

    def grid(self, size=10):
        for x in range(0, conf.WINWIDTH, size):
            self.moveTo((x, 0))
            self.lineTo((x, conf.WINHEIGHT))

        for y in range(0, conf.WINWIDTH, size):
            self.moveTo((0, y))
            self.lineTo((conf.WINWIDTH, y))

    def wander(self, steps=250, maxDeltaDeg=7, bias=0,
                    maxDist=5, trap=1, spot=0, tail=0):
        if tail:
            tailPenguin = Penguin(self.window)
            tailPenguin.set_visible(0)
            tailPenguin.set_color(BLACK)
            tails = []
        while steps:
            deg = self.path.get_deg()
            deltaDeg = (random.random() * 2 *
                            maxDeltaDeg) - maxDeltaDeg + bias
            self.turnTo(deg + deltaDeg)

            if trap:
                deg = self.path.get_deg()
                x, y = self.get_position()
                xMax, yMax = conf.WINWIDTH, conf.WINHEIGHT
                if x < 90:
                    xc = 90 - x
                    d = 180 - deg
                    da = abs(d)
                    sign = d / da
                    if 180-xc < deg < 180+xc:
                        d = xc
                        self.turnTo(180 - (sign*d))
                if y < 90:
                    yc = 90 - y
                    d = 90 - deg
                    da = abs(d)
                    sign = d / da
                    if 90-yc < deg < 90+yc:
                        d = yc
                        self.turnTo(90 - (sign*d))
                if x > xMax-90:
                    #print 'x %s' %x
                    xc = 90 - (xMax - x)
                    d = 360 - deg
                    da = abs(d)
                    sign = d / da
                    #print 'xc %s deg %s' % (xc, deg)
                    if deg < xc:
                        #print 'SMALL'
                        d = xc
                        self.turnTo(d)
                    if deg > 360-xc:
                        #print 'BANG'
                        d = 360-xc
                        self.turnTo(d)
                if y > yMax-90:
                    yc = 90 - (yMax - y)
                    d = 270 - deg
                    da = abs(d)
                    sign = d / da
                    if 270-yc < deg < 270+yc:
                        d = yc
                        self.turnTo(270 - (sign*d))

            if tail:
                tails.append(self.get_position())
                if len(tails) > tail:
                    tailPenguin.lineTo(tails.pop(0))

            dist = (random.random() * maxDist)
            self.forward(dist)

            if spot:
                self.circle(spot * dist, width=0)

            steps -= 1

        if tail:
            while tails:
                tailPenguin.lineTo(tails.pop(0))
                if self.visible:
                    self.udraw()

    def rose(self, s1=20, length=200, w=50, width=0, color=None):
        if color is not None:
            self.set_color(color)
        pen = self.pen
        self.penUp()
        for a in range(30):
            if color == 'random':
                self.set_color('random')
            self.forward(s1)
            self.rectangle(length, w, width=width)
            self.right(-12)
        if pen:
            self.penDown()

    def wordRose(self, text='wordRose()', s1=20, fontSize=40, color=None):
        if color is not None:
            self.set_color(color)
        pen = self.pen
        self.penUp()
        for a in range(30):
            if color == 'random':
                self.set_color('random')
            self.forward(s1)
            self.write(text, fontSize=fontSize)
            self.right(-12)
        if pen:
            self.penDown()

    def updown(self, w=20, width=0, color=None):
        if color is not None:
            self.set_color(color)
        self.moveTo((0, conf.WINHEIGHT/2))
        self.turnTo(0)
        x = 0
        while x < conf.WINWIDTH:
            if color=='random':
                self.set_color('random')
            self.left(90)
            h = random.randint(1, conf.WINHEIGHT/2)
            self.rectangle(h, w, clockwise=1, width=0)
            self.right(180)
            self.rectangle(h, w, clockwise=0, width=0)
            self.left(90)
            self.forward(w)
            x += w

    def circleWrite(self, message='Write around a circle!'):
        pen = self.pen
        self.penUp()
        message += '  '
        w = self.write(message[0])
        angle = 360.0 / len(message)
        self.forward(w)
        self.right(angle)
        for letter in message[1:]:
            self.write(letter)
            self.forward(w)
            self.right(angle)
        if pen:
            self.penDown()

    def slowWrite(self, message='Write slowly....', delay=500):
        p = self.get_position()
        pen = self.pen
        self.penUp()
        for letter in message:
            w = self.write(letter)
            pygame.time.wait(delay)
            self.forward(w)
        self.moveTo(p)
        if pen:
            self.penDown()

    def blast(self, radius=100, width=5, speed=2,
                color=None, position=None, delay=10):
        if color is not None:
            save_color = self.color
            self.set_color(color)
        if position is not None:
            self.set_position(position)
        to = pygame.time.get_ticks()
        for r in range(1, radius+(speed*width)+speed, speed):
            t = pygame.time.get_ticks()
            if t - to < delay:
                pygame.time.wait(delay - (t - to))
            to = t
            if r < radius - width:
                self.cCircle(r+speed)
            if r > (speed*width):
                self.cCircle(r-(speed*width), color=self.bgColor)
        if color is not None:
            self.set_color(save_color)

    def innerCircle(self, radius=155, irFactor=0.4, skip=2):
        pen = self.pen
        self.penUp()
        self.forward(radius)
        self.right(90)
        d = radius * math.sin(PIx2 / 360)
        skip0 = skip

        ir = 1
        for a in range(360):
            if not skip:
                self.circle(ir)
                skip = skip0
            skip -= 1
            ir += radius * irFactor / 360.0
            self.forward(d)
            self.right(1)

        if pen:
            self.penDown()

    def innerFlow(self, radius=185, irFactor=0.55, skip=3,
                    color0='random', color1='random'):
        pen = self.pen
        color = self.color
        if color0 == 'random':
            self.set_color('random')
            color0 = self.color
        if color1 == 'random':
            self.set_color('random')
            color1 = self.color
        r0, g0, b0 = color0
        r1, g1, b1 = color1
        rs, gs, bs = [(r1 - r0) / 360.0,
                        (g1 - g0) / 360.0,
                        (b1 - b0) / 360.0]
        self.penUp()

        d = radius * math.sin(PIx2 / 360)
        skip0 = skip

        ir = 1
        for a in range(360):
            if not skip:
                r, g, b = (int(r0 + rs * a),
                            int(g0 + gs * a),
                            int(b0 + bs * a))
                self.set_color((r, g, b))
                self.circle(ir)
                skip = skip0
            skip -= 1
            ir += radius * irFactor / 360.0
            self.forward(d)
            self.right(1)

        self.set_color(color)
        if pen:
            self.penDown()

    def yinyang(self, radius=None, position=None, direction=None):
        pen = self.pen
        self.penUp()
        color = self.color

        if radius is None:
            radius = conf.WINHEIGHT / 2.0
        diameter = 2 * radius
        if position is not None:
            self.moveTo(position)

        self.cCircle(radius)
        if direction is not None:
            self.turnTo(direction)
        a = self.get_deg()
        self.forward(radius)
        self.right(90)

        d = radius * math.sin(PIx2 / 900.0)

        a0 = a
        while a < 180 + a0:
            th = ((a - a0) / 180.0) * PI / 2
            ir = 0.25 * diameter * math.sin(th) * math.sin(th) + 1
            self.circle(ir, width=0)
            self.forward(d)
            self.right(0.4)
            a += 0.4

        self.right(90)
        self.forward(diameter / 4.0)
        self.cCircle(diameter / 20.0, color=self.bgColor, width=0)
        self.forward(diameter / 2.0)
        self.cCircle(diameter / 20.0, color=color, width=0)

        if pen:
            self.penDown()
        self.set_color(color)

    def yinyangs(self, n=15, radius=65):
        for yy in range(n):
            self.moveTo('random')
            self.turnTo('random')
            self.yinyang(radius)

    def yinyin(self, n=5, radius=None):
        for turn in range(n):
            self.home()
            self.set_color('random')
            self.yinyang(radius)
            self.home()
            self.set_color('random')
            self.right(180)
            self.yinyang(radius)

    def twist(self, angle=89.8, mult=1.01, colors=[RED, WHITE, RED, BLUE],
                    size0=1, size=conf.WINWIDTH):
        colorNumber = 0
        numColors = len(colors)

        if mult < 0:
            mult = abs(mult)
        #if mult < 1:
        #    mult += 1
        side=size0
        while side < size:
            self.set_color(colors[colorNumber%numColors])
            self.forward(side)
            self.right(angle)
            side *= mult
            colorNumber += 1

    def crescent(self):
        r0 = conf.WINWIDTH / 2
        y = 0
        while y < r0:
            self.moveTo((0, 0))
            r = math.hypot(r0, y)
            angle = math.atan2(r0, y)
            deg = angle * (360 / PIx2)
            self.turnTo(-deg)
            perc = 2 * angle/ PIx2
            #print perc
            arc = PIx2 * r * perc
            #print arc
            side = arc / 90
            #print side
            a = (2 * angle / 90) * (360 / PIx2)
            #print a
            for s in range(90):
                self.forward(side)
                self.left(a)
            y += 20

    def squareTwist(self):
        for size in range(conf.WINWIDTH, 10, -10):
            self.cSquare(size, color='random', width=0)
            self.right(2)

    def circleSquares(self):
        color = self.color
        d = conf.WINWIDTH
        while d > 20:
            self.cSquare(d, color=color, width=0)
            self.cCircle(d/2, color=BLACK, width=0)
            d = d / math.sqrt(2)

    def jag(self, step=2):
        y = random.randrange(0, conf.WINHEIGHT)
        x = 0
        self.moveTo((x, y))
        for x in range(0, conf.WINWIDTH, step):
             y = random.randrange(0, conf.WINHEIGHT)
             self.lineTo((x, y))

    def curve(self, steps=100, color=None):
        c = self.color
        if color is not None:
            self.set_color(color)
        stepX = float(conf.WINWIDTH) / steps
        stepY = float(conf.WINHEIGHT) / steps
        for step in range(steps):
            self.moveTo(((conf.WINWIDTH - (step * stepX)), 0))
            self.lineTo((0, (step * stepY)))
        if c is not None:
            self.set_color(c)

    def spill(self, colors=None, width=0):
        r = conf.WINWIDTH
        while r > 5:
            if colors is None:
                self.set_color('random')
            else:
                self.set_color(random.choice(colors))
            self.moveTo((r, r))
            self.cCircle(r, width=0)
            r -= 5

    def sine(self, size=70, cycles=3, color=None, delay=30):
        if color is not None:
            save_color = self.color
            self.set_color(color)
        cycles = abs(cycles)
        a = 0
        r = 5
        rOld = 5
        to = pygame.time.get_ticks()
        while cycles:
            self.move()
            t = pygame.time.get_ticks()
            if t - to < delay:
                pygame.time.wait(delay - (t - to))
            to = t
            r = int(abs(size * math.sin(a)) + 5)
            self.cCircle(r)
            if rOld != r:
                self.cCircle(rOld, self.bgColor)
            rOld = r
            a += 0.04
            if a > PIx2:
                cycles -= 1
                a = 0
                if color is not None:
                    self.set_color(color)
        if color is not None:
            self.set_color(save_color)

    def sineWave(self, waves=7, amprct=80):
        w, h = conf.WINWIDTH, conf.WINHEIGHT
        x = 0
        y = h / 2
        self.moveTo((x, y))
        
        waveLength = (float(w) / waves)
        amplitude = (amprct / 100.0) * (h / 2)
        while x < w:
            y = (math.sin(PIx2 * x / waveLength) * amplitude) + (h / 2)
            
            # I wanted him to point along the path,
            # but it is not working right. Help!
            rad = -((amplitude/9.5) * PIx2/waveLength) * math.cos(PIx2 * x / waveLength)
            #print rad
            deg = rad * (360.0 / PIx2)
            self.turnTo(deg)
            self.lineTo((x, y))
            x += 1                   
    
    def squareWave(self, waves=20, amprct=80):
        w, h = conf.WINWIDTH, conf.WINHEIGHT
        x = 0
        y = h / 2
        self.moveTo((x, y))
        self.turnTo(0)
        
        waveLength = w / waves
        amplitude = (amprct / 100.0) * (h / 2)
        while x < w:
            self.left(90)
            self.forward(amplitude)
            self.right(90)
            self.forward(waveLength / 2)
            self.right(90)
            self.forward(amplitude)
            self.forward(amplitude)
            self.left(90)
            self.forward(waveLength / 2)
            self.left(90)
            self.forward(amplitude)
            self.right(90)
            x, y = self.get_position()

    def moire(self, step=4):
        self.moveTo('random')
        pos = self.get_position()
        y = 0
        for x in range(0, conf.WINWIDTH, step):
            self.lineTo((x, y))
            self.moveTo(pos)
        x = conf.WINWIDTH
        for y in range(0, conf.WINHEIGHT, step):
            self.lineTo((x, y))
            self.moveTo(pos)
        y = conf.WINHEIGHT
        for x in range(conf.WINWIDTH, 0, -step):
            self.lineTo((x, y))
            self.moveTo(pos)
        x = 0
        for y in range(conf.WINHEIGHT, 0, -step):
            self.lineTo((x, y))
            self.moveTo(pos)

    def star(self, points=7, r=200, ri=50, fill=0, position=None):
        if position is None:
            x, y = self.get_position()
        else:
            x, y = position

        eachangle = PIx2 / points
        half = eachangle / 2
        angles = [z * eachangle for z in range(points)]

        xfirst, yfirst = x, y + r
        self.moveTo((xfirst, yfirst))

        if fill:
            self.begin_fill()

        for i in range(len(angles)):
            angle = angles[i]
            angleprev = angles[i-1]
            x0, y0 = (x + (r * math.sin(angle)),
                        y + (r * math.cos(angle)))
            x1, y1 = (x + (ri * math.sin(angle + half)),
                        y + (ri * math.cos(angle + half)))
            x2, y2 = (x + (ri * math.sin(angle - half)),
                        y + (ri * math.cos(angle - half)))
            self.lineTo((x0, y0))
            self.lineTo((x1, y1))

        self.lineTo((xfirst, yfirst))
        if fill:
            self.commit_fill()

        self.moveTo((x, y))

    def starrose(self, points=None, fade=None):
        vis = self.visible
        self.hide()
        position = self.get_position()

        if points is None:
            points = random.randrange(9, 45)
        
        r, g, b = self.color
        if fade != 'all':
            if r > g  and r > b:
                fade = 'red'
            elif g > r and g > b:
                fade = 'green'
            else:
                fade = 'blue'

        for ri in range(150, 1, -1):
            if fade == 'red' or fade == 'all':
                fr = int((ri/150.0) * r)
            else:
                fr = r

            if fade == 'green' or fade == 'all':
                fg = int((ri/150.0) * g)
            else:
                fg = g

            if fade == 'blue' or fade == 'all':
                fb = int((ri/150.0) * b)
            else:
                fb = b

            self.set_color((fr, fg, fb))
            self.star(points, ri=ri, fill=1, position=position)
            self.moveTo(position)

        self.set_visible(vis)

    def starryNight(self, stars=40, biggest=50, smallest=5):
        for c in range(stars):
            points = random.randint(5, 25)
            r = random.randint(smallest, biggest)
            ri = random.randint(int(.3 * r), int(.7 * r))
            fill = random.randint(0, 1)
            self.set_color('random')
            self.moveTo('random')
            self.star(points, r, ri, fill=fill)

    def gradient(self, c1=None, c2=BLACK):
        if c1 is None:
            c1 = self.color
        
        nsteps = conf.WINWIDTH
        r0, g0, b0 = c1
        dred = float(c2[0] - c1[0]) / nsteps
        dgreen = float(c2[1] - c1[1]) / nsteps
        dblue = float(c2[2] - c1[2]) / nsteps
        
        for x in range(nsteps):
            r = r0 + int(x*dred)
            g = g0 + int(x*dgreen)
            b = b0 + int(x*dblue)
            self.set_color((r, g, b))
            
            self.moveTo((x, 0))
            self.lineTo((x, conf.WINHEIGHT))
        
        self.set_color(c1)

    def backgrounds(self):
        for a in range(9):
            self.cSquare(200)
            self.right(6)
        
        for color in COLORS:
            self.set_background(color)

    def transactions(self):
        self.star()
        self.begin(interactive=1)
        self.star(ri=45)
        self.rollback()
        self.begin() # defaults to interactive
        self.star(ri=55)
        self.commit()
        self.begin(interactive=0)
        self.cCircles()
        self.commit()

    def cellular(self, code="04444333221", cellsize=4):
        """Adapted from code posted to
        edu-sig@python.org by Gregor Lingl"""

        w, h = conf.WINSIZE
        cols = w/cellsize
        lines = h/cellsize

        code = code[:13]
        code = code + "0"*(13-len(code))
        world = []
        topline = [0]*cols
        topline[cols/2] = 1
        for z in range(lines):
            world.append(topline)
            newline = [0]*cols
            for s in range(1, cols-1):
                sum = topline[s-1] + topline[s] + topline[s+1]
                newline[s] = int(code[sum])
            topline = newline

        for y in range(lines):
            for x in range(cols):
                color = COLORS[world[y][x]]
                self.moveTo((x*cellsize, y*cellsize))
                self.square(cellsize, color=color, width=0)

    def lindenmayer(self, axiom="F", regulator={"F":"FF+[+F-F-F]-[-F+F+F]"},
                    deep=3, walked=9, angle=180/8.0, startpos=None, startdeg=None):
        """Adapted from code posted to
        edu-sig@python.org by Gregor Lingl"""

        self.tstack = []

        def l():
            self.left(self.angle)
        def r():
            self.right(self.angle)
        def turn():
            self.left(180)

        def bigger():
            self.step *= 2
        def smaller():
            self.step /= 2

        def f():
            self.penUp()
            self.forward(self.step)
        def F():
            self.penDown()
            self.forward(self.step)

        def save():
            self.tstack.append((self.get_position(), self.get_deg()))
        def load():
            position, deg = self.tstack.pop()
            self.moveTo(position)
            self.turnTo(deg)

        regulate = {"-":l, "+":r, "F": F, "f":f, ">":bigger, "<":smaller,
                        "|": turn, "[":save, "]":load}

        def replace(follow, regulator, n):
            for i in range(n):
                newfollow = ""
                for element in follow:
                    newfollow += regulator.get(element, element)
                follow = newfollow
            return follow

        if startpos is not None:
            self.moveTo(startpos)
        if startdeg is not None:
            self.turnTo(startdeg)

        self.step = walked
        self.angle = angle

        design = replace(axiom, regulator, deep)
        for b in design:
            try:
                regulate[b]()
            except KeyError:
                pass

    def varoom(self, n=30):
        rnudge = 5
        bnudge = 8
        gnudge = 3
        step = 6
        a = 16

        c = 0
        while 1:
            if n > 0:
                c += 1
                if c >= n:
                    break

            self.home()
            self.nudge_color(red=rnudge, blue=bnudge, green=gnudge)
            self.swirl(a=a, n=400)
            r, g, b = self.color
            if r > 250 or r < 5:
                rnudge = -rnudge
            if g > 250 or g < 5:
                gnudge = -gnudge
            if b > 250 or b < 5:
                bnudge = -bnudge
            if a > 170 or a < 16:
                step = -step
            a += step

    def squarewaves(self):
        for a in range(1, 100):
            self.set_color('random')
            self.squareWave(amprct=a)

    def writeFuncName(self, funcName):
        color = self.color
        self.set_color(WHITE)
        self.moveTo((20, 40))
        self.turnTo(0)
        self.write(funcName+'()')
        self.home()
        self.set_color(color)

    def testfuncs(self):
        funcs = ['cCircles', 'rCircles', 'spiral', 'cSpiral',
                    'rStar', 'trouble', 'swirl', 'storm', 'tree',
                    'grid', 'wander', 'rose', 'updown', 'circleWrite',
                    'slowWrite', 'blast', 'innerCircle', 'twist',
                    'crescent', 'wordRose', 'squareTwist', 'circleSquares',
                    'jag', 'curve', 'spill', 'sine', 'innerFlow', 'yinyang',
                    'squareWave', 'sineWave', 'moire', 'star', 'starrose',
                    'starryNight', 'gradient', 'backgrounds', 'transactions',
                    'cellular', 'lindenmayer', 'yinyin', 'yinyangs', 'varoom',
                    'squarewaves', 'rcSpiral']
        return funcs

    def test(self):
        funcs = self.testfuncs()
        random.shuffle(funcs)

        for func in funcs:
            self.reset()
            self.set_color('random')

            self.writeFuncName(func)

            f = getattr(self, func)
            f()

            self.writeFuncName(func)

            time.sleep(5)


class DemoPenguin(Penguin):
    def set_demo(self, demo):
        self.demo = demo
        self.move = self.demomove

    def demomove(self):
        self.demo.checkEvents()
        Penguin.move(self)

class SkipTest(Exception):
    pass

class PenguinDemo(Game):
    def __init__(self):
        self._in_test = 0
        Game.__init__(self)

    def skipfunc(self, ev=None):
        raise SkipTest

    def hide(self, ev=None):
        if self.pete.visible:
            self.pete.hide()
        else:
            self.pete.uclear()
            self.pete.show()

    def resize_reset(self):
        self.pete.window = conf.window
        self.events.kill()
        self.initialize()
        self.pete.center()
        self.pete.set_home()
        self.resized = 1

    def configure(self, ev=None):
        self.resized = 0
        Game.configure(self, None)
        if self.resized:
            self.resized = 0
        if self._in_test:
            raise SkipTest

    def initialize(self):
        Game.initialize(self)
        self.pete = DemoPenguin()
        self.pete.set_demo(self)

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
    
    def mainloop(self, funcs=None):
        if funcs is None:
            funcs = self.pete.testfuncs()
            random.shuffle(funcs)

            funcs.insert(0, 'welcome')

        self._in_test = 1
        for func in funcs:
            try:
                vis = self.pete.visible
                self.pete.reset()
                if not vis:
                    self.pete.hide()

                self.pete.set_color('random')

                self.pete.writeFuncName(func)

                f = getattr(self.pete, func)
                f()

                self.pete.writeFuncName(func)

                self.checkEvents()

                self.waitFor(timeout=2500)

                if self.quit:
                    break

            except SkipTest:
                self.pete.rollback_fill()
                self.pete.rollback()


if __name__ == '__main__':
    demo = PenguinDemo()

    if len(sys.argv) > 1:
        funcs = sys.argv[1:]
    else:
        funcs = None

    demo.mainloop(funcs)
