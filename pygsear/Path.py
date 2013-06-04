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

"""Ways for things to move around on screen

"""

import math
import random
import os

import pygame
from pygame.locals import QUIT, KEYUP, K_ESCAPE

import conf
import Util
from locals import PI, PIx2


class EndOfPath(Exception):
    """Raise at the end of a path."""

    pass

class Path:
    """A set of points."""

    def __init__(self, position=(0, 0), duration=None):
        """Initialize the Path

        @param position: initial coordinates
        @param duration: Seconds until Path should raise C{StopIteration}

        """

        self.position = [0, 0]
        self.positionOld = [0, 0]
        self.set_position(position)
        self.positionOld = self.position[:]
        self.directionOld = 0.0
        self.duration = duration
        self.set_endTime()
        self.paused = None

    def set_endTime(self, duration=None):
        """Path will raise StopIteration after self.duration seconds

        @param duration: Seconds until Path should raise C{StopIteration}.
            If duration is not specified (or is None) uses
            C{self.duration} so that C{set_endTime()} can be used to
            reset the C{Path} duration counter.

        """

        if duration is not None:
            self.duration = duration
        if self.duration is not None:
            self.endTime = pygame.time.get_ticks() + self.duration * 1000
        else:
            self.endTime = None

    def __iter__(self):
        return self

    def set_position(self, position):
        """Set position and update positionOld

        For many paths, this position will be overridden
        by the next call to next() and so it will never
        be seen.

        Also, many Drawable objects maintain their own position
        and so a call to that object's set_position may be more
        appropriate.

        """

        self.positionOld[0], self.positionOld[1] = self.position[0], self.position[1]
        self.position[0], self.position[1] = position[0], position[1]

    def get_position(self):
        """Return position along Path"""

        return self.position[0:2]

    def get_direction(self):
        """Return the direction from the previous location to the current location.

        """

        x, y = self.get_position()
        xOld, yOld = self.positionOld
        dx = x - xOld
        dy = y - yOld
        direction = math.atan2(-dy, dx)
        #print dx, dy, direction
        if dx or dy:
            self.directionOld = direction
            return direction
        else:
            return self.directionOld

    def get_x(self):
        """return x component of position"""

        return self.position[0]

    def get_y(self):
        """return y component of position"""

        return self.position[1]

    def next(self):
        """return position

        @raises StopIteration: If duration has expired, or
        if position has been set to (None, None)

        """

        stop = 0
        if self.endTime is not None:
            t = pygame.time.get_ticks()
            if t > self.endTime:
                stop = 1
        position = self.get_position()
        if position == (None, None):
            stop = 1
        if stop:
            raise StopIteration
        else:
            return position

    def reset(self):
        """put path back to original state"""

        if self.duration is not None:
            self.set_endTime()

    def pause(self):
        """stop moving along path"""

        self.paused = pygame.time.get_ticks()

    def unpause(self):
        """resume moving along path"""

        self.paused = None
        self.ticks = pygame.time.get_ticks()

    def onscreen(self, slack=0):
        """true if path position is on main window

        Drawable objects should be using the C{pygsear.Drawable.onscreen} instead.

        @param slack: position can be this far off window and still return True.

        """

        x, y = self.get_position()
        minX = -slack
        minY = -slack
        maxX = conf.WINWIDTH + slack
        maxY = conf.WINHEIGHT + slack

        if (x >= minX and y >= minY and
                x <= maxX and y <= maxY):
            return 1
        else:
            return 0


class PathNG(Path):
    """Next-generation Path

    This one will integrate all of these disparate Path subclasses
    in to one uberclass. I think this will make it more usable.

    """

    def __init__(self, startLocation=(100, 100),
                    vx=0, vy=0,
                    ax=0, ay=0,
                    gx=0, gy=0, # gx, gy is constant accel part (ie gravity)
                    duration=None):
        Path.__init__(self, startLocation, duration=duration)
        self.set_startLocation(startLocation)
        self.set_startVelocity((vx, vy))
        self.set_startAcceleration((ax, ay))
        self.set_gravity(gx, gy)
        self.set_restriction()
        self.reset()

    def reset(self):
        """Go back to initial position, velocity and acceleration

        #Also updates self.ticks to current time

        """

        self._direction = 0

        self.set_position(self.startLocation)
        self.set_velocity(vx=self.vx0, vy=self.vy0)
        self.set_acceleration(ax=self.ax0, ay=self.ay0)
        #self.set_gravity(self.gx0, self.gy0)

        self.speed_sign = 1

        self.set_turnRate()

        #self.ticks = pygame.time.get_ticks()

    def set_restriction(self, onscreen=None, **kw):
        """Set a constraint on the path.

        Restrictions are set as keyword arguments. So far these are
        the contraints that work:
            - speed: maximum speed

            - xMin: minimum x-value
            - yMin: minimum y-value
            - xMax: maximum x-value
            - yMax: maximum y-value

            - vxMin: minimum x-velocity (remember negative values)
            - vyMin: minimum y-velocity
            - vxMax: maximum x-velocity
            - vyMax: maximum y-velocity

        @param onscreen: set to nonzero value if the object should be limited
            to staying on the screen.

        """

        #print 'onscreen', onscreen
        if onscreen is not None:
            self.restriction['xMin'] = 0
            self.restriction['yMin'] = 0
            self.restriction['xMax'] = conf.WINWIDTH
            self.restriction['yMax'] = conf.WINHEIGHT

        if not hasattr(self, 'restriction'):
            self.restriction = {    'speed': 2000,

                                    'vxMax': 5000,
                                    'vxMin': -5000,
                                    'vyMax': 5000,
                                    'vyMin': -5000,

                                    'xMax': None,
                                    'xMin': None,
                                    'yMax': None,
                                    'yMin': None,
                                }

        for side, val in kw.items():
            #print side, val
            self.restriction[side] = val

    def show_restrictions(self):
        if hasattr(self, 'restriction'):
            for key, val in self.restriction.items():
                print key, val
        else:
            print 'no restrictions set'

    def set_startLocation(self, location=None):
        """Set location to go back to on reset()


        @param location: (x, y) position
            If location is not given (or None), sets startLocation to
            current location.

        """

        if location is None:
            location = self.get_position()
        self.startLocation = location

    def set_startVelocity(self, vel=None):
        """Set velocity to go back to on reset()

        @param vel: (vx, vy) horizontal and vertical velocity components

        """

        if vel is None:
            vel = self.get_velocity()
        self.vx0, self.vy0 = vel

    def set_startAcceleration(self, accel=None):
        """Set acceleration to back go to on reset()

        @param accel: (ax, ay) horizontal and vertical acceleration components

        """

        if accel is None:
            accel = self.get_acceleration()
        self.ax0, self.ay0 = accel

    def _set_velocity(self, vx=None, vy=None):
        if vx is not None:
            self.vx = vx
        if vy is not None:
            self.vy = vy

    def set_velocity(self, special=None, vx=None, vy=None):
        """Set velocity

        @param special: Set to 'random' for a random velocity
        @param vx: horizontal velocity component
        @param vy: vertical velocity component

        """

        vxMax = self.restriction['vxMax']
        vxMin = self.restriction['vxMin']
        vyMax = self.restriction['vyMax']
        vyMin = self.restriction['vyMin']
        max_speed = self.restriction['speed']

        if special == 'random':
            if vx is None:
                vx = random.uniform(vxMin, vxMax)
            if vy is None:
                vy = random.uniform(vyMin, vyMax)

        if vx is not None:
            vx = max(vx, vxMin)
            vx = min(vx, vxMax)
        if vy is not None:
            vy = max(vy, vyMin)
            vy = min(vy, vyMax)

        self._set_velocity(vx, vy)

        speed = self.get_speed()
        if speed > max_speed:
            self.set_speed(max_speed)

    def get_velocity(self):
        """return velocity"""

        return self.vx, self.vy

    def get_speed(self):
        """return speed"""

        vx = self.vx
        vy = self.vy
        return math.hypot(vx, vy)

    def set_speed(self, speed=None, change=None):
        """Change speed while keeping the same direction of movement.

        @param speed: New speed (must set speed OR change)
        @param change: Change in speed (must set speed OR change)

        """

        if (speed is None and change is None) or (speed is not None and change is not None):
            raise TypeError, 'must give speed or acceleration'

        d = self.get_direction()
        sign = self.speed_sign
        if speed is not None:
            if speed < 0:
                self.speed_sign = -1
                if sign >= 0:
                    d += PI
                speed = abs(speed)

            else:
                self.speed_sign = 1

            vx = speed * math.cos(d)
            vy = -speed * math.sin(d)
            self._set_velocity(vx, vy)

        else:
            speed = self.get_speed()
            speed += change
            self.set_speed(speed)

    def get_direction(self):
        """return direction of travel

        Direction is given in radians. 0 radians is towards the right
        edge of the screen.

        """

        vx = self.vx
        vy = self.vy

        if vx and vy:
            direction = math.atan2(-self.vy, self.vx)
            self._direction = direction
        else:
            direction = self._direction

        return direction

    def set_direction(self, direction):
        """set direction of travel

        Maintains current speed.

        """

        s = self.get_speed()
        vx = s * math.cos(direction)
        vy = s * math.sin(direction)
        self.set_velocity(vx=vx, vy=-vy)

    def distance(self, point):
        """return distance to a point"""

        x, y = self.get_position()
        x1, y1 = point

        return math.hypot((x1 - x), (y1 - y))

    def direction(self, point):
        """return direction to a point"""

        x, y = self.get_position()
        x1, y1 = point

        return math.atan2(-(y1 - y), (x1 - x))

    def set_turnRate(self, turnRate=0):
        """set turn rate in rad/s"""

        self.turnRate = turnRate

    def turn(self, rad=None):
        """turn to the left by radians"""

        #print rad
        direction = self.get_direction()
        #print 'dr', direction, rad
        self.set_direction(direction + rad)

    def turn_right(self):
        self.set_turnRate(-1)

    def turn_left(self):
        self.set_turnRate(1)

    def turn_straight(self):
        self.set_turnRate()

    def turn_towards(self, point):
        """turn as quickly as possible towards a point"""

        direction = self.direction(point)
        moving = self.get_direction()

        rad = (moving - direction) % PIx2

        if rad > PI:
            rad -= PIx2
        elif rad < -PI:
            rad += PIx2

        if rad > 0.1:
            self.turn_right()
        elif rad < -0.1:
            self.turn_left()
        else:
            self.turn_straight()

    def set_acceleration(self, ax=None, ay=None):
        """Set acceleration. Change in speed depends on the
        acceleration and the time between frames.

        @param ax: horizontal acceleration component
        @param ay: vertical acceleration component

        """

        if ax is not None:
            self.ax = ax
            self.dex = False
        if ay is not None:
            self.ay = ay
            self.dey = False

    def accelerate(self, acc):
        """Accelerate in the direction currently moving.

        Accelerates toward 0 (right side of screen) if not moving.

        """

        direction = self.get_direction()
        ax = acc * math.cos(direction)
        ay = acc * math.sin(direction)

        self.set_acceleration(ax=ax, ay=ay)

    def get_acceleration(self):
        """return acceleration

        Note that the acceleration may actually be a deceleration.

        """

        return self.ax, self.ay

    def set_deceleration(self, dex=None, dey=None):
        """Set deceleration. Like acceleration, but acts to oppose
        the current velocity and will not change a 0 velocity.

        Can only accelerate or decelerate in a particular direction.

        Note that when using deceleration, the ax or ay value is always
        kept as an absolute value and a deceleration flag. There is no
        way to do "negative acceleration".

        @param dex: horizontal acceleration component
        @param dey: vertical acceleration component

        """

        vx, vy = self.get_velocity()
        if dex is not None:
            self.ax = abs(dex)
            self.dex = True
        if dey is not None:
            self.ay = abs(dey)
            self.dey = True

    def decelerate(self, dec):
        """Decelerate according to the direction currently moving.

        """

        direction = self.get_direction()
        dex = dec * math.cos(direction)
        dey = dec * math.sin(direction)

        self.set_deceleration(dex=dex, dey=dey)

    def set_gravity(self, gx=None, gy=None):
        """Set constant portion of acceleration (ie gravity)

        @param gx: horizontal acceleration component
        @param gy: vertical acceleration component

        """

        if gx is not None:
            self.gx = gx
        if gy is not None:
            self.gy = gy

    def next(self, t=None):
        """return next position along path"""

        if t is None:
            #             ticks = pygame.time.get_ticks()
            #             dt = min(ticks - self.ticks, conf.MAX_TICK)
            #             t = dt / 1000.0
            #             self.ticks = ticks

            ticks = conf.ticks
            dt = min(ticks, conf.MAX_TICK)
            t = dt / 1000.0
            #self.ticks = conf.ticks

        if self.turnRate:
            #print t, self.turnRate, self.turnRate * t
            self.turn(self.turnRate * t)

        sign = self.speed_sign
        vx, vy = self.get_velocity()
        ax, ay = self.get_acceleration()

        if self.dex:
            if vx > 0:
                ax = -ax
        if self.dey:
            if vy > 0:
                ay = -ay

        Ax = self.gx + ax
        Ay = self.gy + ay
        vx = sign * self.vx + (Ax * t)
        vy = sign * self.vy + (Ay * t)

        self.set_velocity(vx=vx, vy=vy)

        x, y = self.get_position()
        x += (vx * t) + (Ax * t**2) / 2
        y += (vy * t) + (Ay * t**2) / 2

        xMax = self.restriction.get('xMax', None)
        xMin = self.restriction.get('xMin', None)
        yMax = self.restriction.get('yMax', None)
        yMin = self.restriction.get('yMin', None)

        #print xMax, xMin

        if xMax is not None:
            #print 'x0', x
            x = min(x, xMax)
            #print 'x1', x
        if xMin is not None:
            x = max(x, xMin)
        if yMax is not None:
            y = min(y, yMax)
        if yMin is not None:
            y = max(y, yMin)

        self.set_position((x, y))
        return Path.next(self)

    def bounce_x(self):
        """reverse travel in x-direction"""

        self.vx = -self.vx

    def bounce_y(self):
        """reverse travel in y-direction"""

        self.vy = -self.vy


class StationaryPath(Path):
    """For things that do not move, but need to be moved sometimes

    Depending on the size of the sprite, and how many other sprites
    there are, you may be better off using a Drawable.Stationary
    object instead, which draws the image directly to the background
    and does not need to be updated every frame.

    """

    def __init__(self, sprite, duration=None):
        Path.__init__(self, duration=duration)
        pos = sprite.get_position()
        self.set_position(pos)
        self.sprite = sprite

    def next(self):
        pos = self.sprite.get_position()
        self.set_position(pos)
        return Path.next(self)


class ListPath(Path):
    """Set of points fully created when instantiated."""

    def __init__(self, places=None, duration=None):
        Path.__init__(self, duration=None)
        if places is None:
            self.places = []
        else:
            self.places = places
        self.place = -1
        self.set_timePerPlace(duration)
        self.set_loop(1)

    def set_timePerPlace(self, duration):
        if duration is not None and duration > 0 and self.places:
            self.perPlace = (float(duration) / len(self.places)) * 1000.0
            self.ticks = pygame.time.get_ticks()
        else:
            self.perPlace = None

    def reset(self):
        Path.reset(self)
        self.set_loop(self.loopStart)
        self.place = -1
        if self.perPlace is not None:
            self.ticks = pygame.time.get_ticks()

    def set_loop(self, loop=1):
        """Set number of times to go around path.

        @param loop: number of times to loop before raising StopIteration
                if -1, loop forever.

        """
        self.loopStart = loop
        self.loop = loop

    def _oneLoop(self):
        """Check if should continue looping."""

        self.place = 0
        if self.loop > 0:
            self.loop -= 1
        if self.loop == 0:
            self.set_position(self.places[self.place])
            raise StopIteration

    def next(self):
        perPlace = self.perPlace
        if perPlace is not None:
            ticks = pygame.time.get_ticks()
            t = ticks - self.ticks
            if t > perPlace:
                while t >= perPlace:
                    self.place += 1
                    t -= perPlace
                self.ticks = ticks
            else:
                pass
        else:
            self.place += 1
        if self.place >= len(self.places):
            self._oneLoop()

        self.set_position(self.places[self.place])
        return self.get_position()


class FilePath(ListPath):
    """Set of points retrieved from a file.

    Format of the file should be:

    (x1, y1)
    (x2, y2)
    (x3, y3)

    where x1, y1, x2, etc are integers. There are no
    special headers or footers in the file, just a
    long list of points, one per line.

    """

    def __init__(self, fileName, duration=None):
        ListPath.__init__(self, duration=duration)
        self.loadLocations(fileName)
        self.set_timePerPlace(duration)

    def loadLocations(self, file):
        self.places = Util.load_points(file)


class LinePath(ListPath):
    """Starts here, goes there, and stops."""

    def __init__(self, startLocation=(100, 100), endLocation=(200, 200),
                    duration=None, steps=200):
        ListPath.__init__(self, duration=duration)

        x0 = startLocation[0]
        y0 = startLocation[1]
        x1 = endLocation[0]
        y1 = endLocation[1]

        dx = float(x1 - x0) / steps
        dy = float(y1 - y0) / steps

        xDistance = abs(x1 - x0)
        xStep = abs(dx)

        places = []
        stepsToTake = steps
        xAdd = 0
        yAdd = 0
        while stepsToTake >= 0:
            places.append((int(x0 + xAdd), int(y0 + yAdd)))
            xAdd += dx
            yAdd += dy
            stepsToTake -= 1

        self.places = places
        self.set_position(self.places[0])
        self.set_timePerPlace(duration)

class BounceLinePath(LinePath):
    """Starts here, goes there, then goes back again."""

    def __init__(self, startLocation=(100, 100), endLocation=(200, 200),
                    duration=None, steps=400):
        LinePath.__init__(self, startLocation, endLocation,
                                duration=duration, steps=int(steps/2))
        places = self.places[:]
        places.reverse()

        self.places += places[1:-1]
        self.set_timePerPlace(duration)

class SquarePath(ListPath):
    """Move in a square.

    Not necessarily aligned horizontally or vertically.

    """

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, size=100, steps=800, clockwise=1):
        ListPath.__init__(self, duration=duration)
        stepsPerSide = int(steps / 4)

        x0 = startLocation[0]
        y0 = startLocation[1]
        direction = startDirection
        self.places = [(x0, y0)]
        for s in range(4):
            x1 = int(x0 + (math.cos(direction) * size))
            y1 = int(y0 - (math.sin(direction) * size))

            path = LinePath((x0, y0), (x1, y1), stepsPerSide)
            self.places += path.places[1:]
            x0 = path.places[-1][0]
            y0 = path.places[-1][1]
            if clockwise:
                direction -= (math.pi / 2)
            else:
                direction += (math.pi / 2)
        self.set_timePerPlace(duration)

    def get_direction(self):
        #print self.positionOld, self.position
        return ListPath.get_direction(self)

class SquareEightPath(ListPath):
    """Two squares, one clockwise, one couterclockwise."""

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, size=100, steps=1600, clockwise=1):
        ListPath.__init__(self, duration=duration)
        stepsPerSquare = int(steps / 2)

        path = SquarePath(startLocation, startDirection, None, size,
                            stepsPerSquare, clockwise)
        places = path.places

        path = SquarePath(startLocation, startDirection, None, size,
                            stepsPerSquare, not clockwise)
        places += path.places[1:-1]

        self.places = places
        self.set_timePerPlace(duration)


class CirclePath(ListPath):
    """Move in a circle."""

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, size=100, steps=400, clockwise=1):
        ListPath.__init__(self, duration=duration)
        x, y = startLocation
        self.direction = startDirection
        self.size = size
        self.steps = steps
        self.clockwise = clockwise

        if clockwise:
            self.cx = x + (math.cos(self.direction - math.pi/2.0) * self.size)
            self.cy = y - (math.sin(self.direction - math.pi/2.0) * self.size)
        else:
            self.cx = x + (math.cos(self.direction + math.pi/2.0) * self.size)
            self.cy = y - (math.sin(self.direction + math.pi/2.0) * self.size)

        places = []
        eachAngle = (math.pi * 2) / steps

        if clockwise:
            toAngle = startDirection + (math.pi / 2)
            eachAngle = -eachAngle
        else:
            toAngle = startDirection - (math.pi / 2)

        for s in xrange(steps):
            placex = int(self.cx + (math.cos(toAngle) * self.size))
            placey = int(self.cy - (math.sin(toAngle) * self.size))

            places.append((placex, placey))
            toAngle += eachAngle

        self.places = places
        self.set_timePerPlace(duration)


class BounceCirclePath(CirclePath):
    """Move in a circle, reverse direction and go back."""

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, size=100, steps=400, clockwise=1):
        CirclePath.__init__(self, startLocation, startDirection, duration,
                                size, steps/2, clockwise)
        places2 = self.places[1:-1]
        places2.reverse()
        self.places += places2
        self.set_timePerPlace(duration)


class ConcentricCirclePath(ListPath):
    """Circles one inside of the other."""

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, minSize=10, maxSize=100, numCircles=3,
                    steps=600, clockwise=1):
        ListPath.__init__(self, duration=duration)
        stepsPerCircle = int(steps / numCircles)
        places = []
        size = minSize
        sizeIncrement = int((maxSize - minSize) / numCircles)
        for c in range(numCircles):
            path = CirclePath(startLocation, startDirection, size,
                                stepsPerCircle, clockwise)
            places += path.places
            size += sizeIncrement
        self.places = places
        self.set_timePerPlace(duration)


class FigureEightPath(ListPath):
    """Move in 2 connected circles, one clockwise, one ccw."""

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, size=100, steps=400, clockwise=1):
        ListPath.__init__(self, duration=duration)
        path1 = CirclePath(startLocation, startDirection, size,
                            steps/2, clockwise)
        path2 = CirclePath(startLocation, startDirection, size, steps/2,
                            not clockwise)
        places = path1.places
        places += path2.places
        self.places = places
        self.set_timePerPlace(duration)


class SuperPath(Path):
    """Used to hold a series of other paths.

    Create paths, then add() the paths to this SuperPath.
    Each path can be repeated 1 or more times.

    """

    def __init__(self, startLocation):
        Path.__init__(self, duration=duration)
        self.paths = []
        self.path = 0
        self.repeat = 0

    def addPath(self, path, repeatCount=1):
        # self.paths is a list of tuples of
        # path, and numbere of times it should repeat
        self.paths.append((path, repeatCount))

    def next(self):
        position = None
        while not position:
            try:
                position = self.paths[self.path][0].next()
            except StopIteration:
                self.repeat += 1
                if self.repeat >= self.paths[self.path][1]:
                    self.path += 1
                    if self.path >= len(self.paths):
                        self.place = 0
                        self.repeat = 0
                        self.path = 0
                        if self.loop > 0:
                            self.loop -= 1
                        elif self.loop == 0:
                            position = self.paths[self.path][0].next()
                            raise StopIteration
                    else:
                        self.repeat = 0
                else:
                    self.place = 0

        self.set_position(position)
        return position


class BrownianPath(Path):
    """Move in random directions

    Moves random amount between + and - maxJump
    in both x and y directions.

    Makes numSteps moves before raising EndPathLoop, or
    continuous moves if numSteps == 0.

    """

    def __init__(self, startLocation=(100, 100), duration=None,
                    maxJump=5, numSteps=0):
        Path.__init__(self, startLocation, duration=duration)
        self.position = startLocation
        self.numSteps = numSteps
        self.steps = 0

        self.stepChoices = [x for x in range(maxJump)]
        self.stepChoices += [x for x in range(0, -maxJump, -1)[1:]]

    def next(self):
        if self.numSteps and self.steps >= self.numSteps:
            self.steps = 0
            if self.loop > 0:
                self.loop -= 1
            elif self.loop == 0:
                raise EndPathLoop
        else:
            self.steps += 1

        dx = random.choice(self.stepChoices)
        dy = random.choice(self.stepChoices)

        x, y = self.position
        x += dx
        y += dy
        self.set_position((x, y))

        return Path.next(self)


class BrownianLinePath(ListPath):
    """Line, with random motion superimposed.

    Need to be careful that maxRandomness does not swamp out
    the motion along the line.

    Might be good to limit maxRandomness to less than distance/steps

    """

    def __init__(self, startLocation=(100, 100), endLocation=(200, 200),
                    maxRandomness=5, steps=10):
        ListPath.__init__(self, duration=duration)

        self.randAdd = [x for x in range(maxRandomness)]
        self.randAdd += [x for x in range(0, -maxRandomness, -1)[1:]]

        x0 = startLocation[0]
        y0 = startLocation[1]
        x1 = endLocation[0]
        y1 = endLocation[1]

        dx = float(x1 - x0) / steps
        dy = float(y1 - y0) / steps

        xDistance = abs(x1 - x0)
        xStep = abs(dx)

        places = []
        stepsToTake = steps
        xAdd = 0
        yAdd = 0
        while stepsToTake >= 0:
            places.append((int(x0 + xAdd), int(y0 + yAdd)))
            xAdd += dx + random.choice(self.randAdd)
            yAdd += dy + random.choice(self.randAdd)
            stepsToTake -= 1

        self.places = places


class VelocityPath(Path):
    """Move according to velocity in pixels per frame."""

    def __init__(self, startLocation=(100, 100), vx=0, vy=0, duration=None):
        Path.__init__(self, startLocation, duration=duration)
        self.set_velocity(vx, vy)

    def next(self):
        x, y = self.position
        position = (x+self.vx, y+self.vy)
        self.set_position(position)
        return Path.next(self)

    def accelerate(self, ax=0, ay=0):
        self.set_velocity(self.vx+ax, self.vy+ay)

    def set_velocity(self, vx=None, vy=None):
        if vx is not None:
            self.vx = vx
        if vy is not None:
            self.vy = vy

    def get_speed(self):
        vx = self.vx
        vy = self.vy
        return math.hypot(vx, vy)

    def get_direction(self):
        return math.atan2(self.vy, self.vx)


class VelocityPathTime(VelocityPath):
    """Move according to velocity in pixels per second."""

    def __init__(self, startLocation=(100, 100), vx=0, vy=0, duration=None):
        VelocityPath.__init__(self, startLocation, vx, vy, duration=duration)
        self.ticks = pygame.time.get_ticks()

    def next(self):
        x, y = self.position
        ticks = pygame.time.get_ticks()
        t = ticks - self.ticks
        #print t
        self.ticks = ticks

        dx = self.vx * (t / 1000.0)
        dy = self.vy * (t / 1000.0)

        position = (x + dx, y + dy)
        self.set_position(position)
        return Path.next(self)


class AccelerationPath(VelocityPath):
    """Move according to vel and accel in pixels per second."""

    def __init__(self, startLocation=(100, 100),
                    vx=0, vy=0,
                    ax=0, ay=0,
                    gx=0, gy=0, # gx, gy is constant accel part (ie gravity)
                    duration=None):
        VelocityPath.__init__(self, startLocation, vx, vy, duration=duration)
        self.vx0, self.vy0 = vx, vy
        self.ax0, self.ay0 = ax, ay
        self.gx0, self.gy0 = gx, gy
        self.reset()

    def reset(self):
        self.set_velocity(self.vx0, self.vy0)
        self.set_acceleration(self.ax0, self.ay0)
        self.set_gravity(self.gx0, self.gy0)
        self.ticks = pygame.time.get_ticks()

    def set_acceleration(self, ax=None, ay=None):
        if ax is not None:
            self.ax = ax
        if ay is not None:
            self.ay = ay

    def set_gravity(self, gx=None, gy=None):
        if gx is not None:
            self.gx = gx
        if gy is not None:
            self.gy = gy

    def next(self, t=None):
        """Use velocity and acceleration info to move sprite,
        and return position.

        @param t: Number of ticks since last update.

        @returns: position.

        """

        if t is None:
            ticks = pygame.time.get_ticks()
            t = ticks - self.ticks
            self.ticks = ticks

        Ax = self.gx + self.ax
        Ay = self.gy + self.ay
        self.vx += Ax * t
        self.vy += Ay * t

        x, y = self.get_position()
        x += (self.vx * t) + (Ax * t**2) / 2
        y += (self.vy * t) + (Ay * t**2) / 2
        self.set_position((x, y))
        return Path.next(self)


class VelocityPathBounded(VelocityPath):
    """VelocityPath with min/max x and y values."""

    def __init__(self, startLocation=(100, 100), vx=0, vy=0, duration=None,
                    xMin=20, xMax=conf.WINWIDTH-20, yMin=20, yMax=conf.WINHEIGHT-20,
                    endPathAtBoundary=1):
        VelocityPath.__init__(self, startLocation, vx, vy, duration=duration)
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.endPathAtBoundary = endPathAtBoundary

    def next(self):
        VelocityPath.next(self)
        self.clamp()
        return Path.next(self)

    def clamp(self):
        x, y = self.position
        hitBoundary = 0
        if x < self.xMin:
            x = self.xMin
            self.vx = -self.vx
            hitBoundary = 1
        elif x > self.xMax:
            x = self.xMax
            self.vx = -self.vx
            hitBoundary = 1
        if y < self.yMin:
            y = self.yMin
            self.vy = -self.vy
            hitBoundary = 1
        elif y > self.yMax:
            y = self.yMax
            self.vy = -self.vy
            hitBoundary = 1

        if hitBoundary:
            pos = (x, y)
            self.set_position(pos)
            if self.endPathAtBoundary:
                raise EndOfPath


class VelocityPathTimeBounded(VelocityPathTime, VelocityPathBounded):
    """VelocityPathTime with min/max x and y values."""

    def __init__(self, startLocation=(100, 100), vx=0, vy=0, duration=None,
                    xMin=20, xMax=conf.WINWIDTH-20, yMin=20, yMax=conf.WINHEIGHT-20,
                    endPathAtBoundary=1):
        VelocityPathTime.__init__(self, startLocation, vx, vy, duration=duration)
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.endPathAtBoundary = endPathAtBoundary

    def next(self):
        VelocityPathTime.next(self)
        VelocityPathBounded.clamp(self)
        return Path.next(self)


class RandomAccelerationPath(VelocityPathTime):
    """Random motion.

    Should be much smoother than BrownianPath since
    acceleration is limited.

    """

    def __init__(self, startLocation=(100, 100), startDirection=0,
                    duration=None, startSpeed=0, maxSpeed=5, minSpeed=0,
                    maxAccel=1):
        self.direction = startDirection
        if startSpeed > maxSpeed:
            self.speed = maxSpeed
        else:
            self.speed = startSpeed
        self.maxSpeed = maxSpeed
        if minSpeed > maxSpeed:
            minSpeed = maxSpeed
        self.minSpeed = minSpeed
        self.maxAccel = maxAccel

        vx = math.cos(startDirection) * self.speed
        vy = -math.sin(startDirection) * self.speed
        VelocityPathTime.__init__(self, startLocation, vx, vy, duration=duration)


    def next(self):
        x, y = self.position
        x += self.vx
        y -= self.vy

        accel = random.random() * self.maxAccel
        accelDirection = random.uniform(0, PIx2)

        ax = math.cos(accelDirection) * accel
        ay = -math.sin(accelDirection) * accel
        self.accelerate(ax, ay)

        speed = self.get_speed()
        if speed > self.maxSpeed:
            speed = self.maxSpeed
        elif speed < self.minSpeed:
            speed = self.minSpeed

        direction = self.get_direction()
        vx = math.cos(direction) * speed
        vy = math.sin(direction) * speed
        self.set_velocity(vx, vy)
        #print direction, speed, vx, vy

        position = (x, y)
        self.set_position(position)

        return VelocityPathTime.next(self)


class RandomAccelerationPathBounded(RandomAccelerationPath, VelocityPathBounded):
    """Random motion, with set location limits."""

    def __init__(self, startLocation=(100,100), startDirection=0, startSpeed=0,
                    duration=None, maxSpeed=5, minSpeed=0, maxAccel=1,
                    xMin=20, xMax=None, yMin=20, yMax=None,
                    endPathAtBoundary=0):
        RandomAccelerationPath.__init__(self, startLocation, startDirection, duration,
                                        startSpeed, maxSpeed, minSpeed, maxAccel)
        self.xMin = xMin
        if xMax is None:
            xMax = conf.WINWIDTH-20
        self.xMax = xMax
        self.yMin = yMin
        if yMax is None:
            yMax = conf.WINHEIGHT-20
        self.yMax = yMax
        self.endPathAtBoundary = endPathAtBoundary

    def next(self):
        RandomAccelerationPath.next(self)
        pos = VelocityPathBounded.clamp(self)
        return Path.next(self)


class Offset_path(Path):
    """Follow another path, possibly moved over some."""

    def __init__(self, path, xOffset=0, yOffset=0):
        Path.__init__(self)
        self.follow(path)
        self.xOffset = xOffset
        self.yOffset = yOffset
        self.path.next()

    def follow(self, path):
        self.path = path

    def next(self):
        x, y = self.path.get_position()
        x += self.xOffset
        y += self.yOffset

        position = x, y
        self.set_position(position)

        return position


class RandomOnscreen(Path):
    """Move to random locations on screen.

    Can also move to random spot inside of box defined by
    xMin, yMin, xMax, xMax.

    stayMax tells how many times the Path will return
    the same location before moving again. If stayMax == -1
    will stay put until the next call to randomMove()

    """

    def __init__(self, duration=None, xMin=0, yMin=0,
                    xMax=conf.WINWIDTH, yMax=conf.WINHEIGHT,
                    stay=None):
        Path.__init__(self, duration=duration)
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        if stay is not None:
            self.stayMax = stay * 1000
            self.stay = self.stayMax
            self.ticks = pygame.time.get_ticks()
        else:
            self.stayMax = None
        self._randomMove()
        self.next()

    def _randomMove(self):
        x = random.randint(self.xMin, self.xMax)
        y = random.randint(self.yMin, self.yMax)
        self.position = (x, y)

    def next(self):
        move = 0
        if self.stayMax is None:
            move = 1
        else:
            ticks = pygame.time.get_ticks()
            t = ticks - self.ticks
            self.ticks = ticks
            self.stay -= t
            if self.stay <= 0:
                self.stay = self.stayMax
                move = 1
        if move:
            self._randomMove()

        return Path.next(self)


class TurtlePath(Path):
    def __init__(self, position=(100, 100), deg=90):
        Path.__init__(self, position)
        self.set_direction((deg % 360) * PI / 180)

    def set_direction(self, direction):
        if abs(direction) < 0.0000001:
            direction = 0
        self.direction = direction % PIx2

    def set_deg(self, deg):
        self.set_direction(PIx2 * deg / 360)

    def get_direction(self):
        return self.direction

    def get_deg(self):
        return self.get_direction() * 360 / PIx2

    def left(self, deg):
        direction = self.get_direction()
        rad = deg * (PI / 180)
        self.set_direction(direction + rad)

    def right(self, deg):
        self.left(-deg)

    def forward(self, dist):
        x, y = self.get_position()
        th = self.get_direction()
        dx = dist * math.cos(th)
        dy = dist * math.sin(th)

        position = x+dx, y-dy
        self.set_position(position)

    def back(self, dist):
        self.forward(-dist)

    def next(self):
        """A questionable hack to let Penguin exit in the middle of the demo.

        """

        for e in pygame.event.get():
            if e.type == QUIT:
                raise SystemExit
            elif e.type == KEYUP and e.key == K_ESCAPE:
                raise SystemExit
        return self.get_position()
