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

"""Things to show on the Pygame display.

"""

import time, random, math, os, types

import pygame
import pygame.draw
from pygame.sprite import Sprite, AbstractGroup, RenderUpdates

import conf
import Screen
import Path
import Util
from Util import load_image, load_images, line_seg_intersect, scale_image
from locals import WHITE, BLACK, TRANSPARENT, LRED
from locals import PI, PIx2



class SpriteGroup(RenderUpdates):
    """Specialized L{pygame.sprite.Group} with more functionality.

    The main advantage of C{SpriteGroup} is that it knows which
    window its sprites live in and can C{draw()} and C{clear()} them
    without needing to pass the screen or background to the
    functions.

    @ivar layer: L{Screen.Layer} in which the sprites live.
        All C{draw()} and C{clear()} operations on the sprites will
        use the layer's C{screen} and C{bg} L{pygame.Surface}s.

    """

    def __init__(self, layer=None, sprites=[]):
        """Initialize the sprite group.

        @param layer: L{Screen.Layer} in which the sprite lives.
        @param sprites: Initial sprite or sequence of sprites in the group.

        """
        self.levels = {0: self}
        if layer is None:
            layer = conf.window


        else:
            pass
            # Need to make sure NOT to use RenderUpdates.draw
            # which will draw using the .rect ????

            # What about sprites in the group that use a different
            # layer than the one provided when the Group was formed ?

        self.layer = layer
        self.screen = layer.screen
        self.bg = layer.bg
        RenderUpdates.__init__(self, sprites)
        #self.add(sprites) # should not be necessary... done in Group.__init__

    def add(self, sprites, level=0):
        """Add sprite to group.

        @param sprites: Either a single sprite, or a sequence of sprites.
        @param level: Drawing layer at which to add the sprite. Higher
            numbers will be drawn after (on top of) lower numbers.  Level can be
            less than 0 to indicate that sprite should be drawn below sprites at
            the default level.

        """

        if level == 0:
            RenderUpdates.add(self, sprites)
        else:
            if not self.levels.has_key(level):
                level_group = SpriteGroup(self.layer)
                self.levels[level] = level_group
            else:
                level_group = self.levels[level]
            level_group.add(sprites)

    def change_level(self, level, to_level):
        """Change the drawing level.

        """

        levels = self.levels
        levels[to_level] = levels[level]
        del(levels[level])

    def clear(self):
        """Clear all of the sprites in the group to the background.

        """

        levels = self.levels.keys()
        levels.sort()
        for l in levels:
            level = self.levels[l]
            RenderUpdates.clear(level, self.screen, self.bg)


    def clear_layer(self):
        """Not used at this time.

        """

        for sprite in self.sprites():
            if len(self.levels) > 1:
                levels = self.levels.keys()
                levels.sort()
                for l in levels[1:]:
                    level = self.levels[l]
                    RenderUpdates.clear(level, self.screen, self.bg)


    def draw(self):
        """draw(surface)
        draw all sprites onto the surface

        Draws all the sprites onto the given surface. It
        returns a list of rectangles, which should be passed
        to pygame.display.update()

        """

        r = []
        levels = self.levels.keys()
        levels.sort()
        for l in levels:
            level = self.levels[l]
            r += RenderUpdates.draw(level, self.screen)

        return r

    def draw_visible(self, surface=None):
        """Draw sprites which are not marked hidden

        Looks for a .hidden property on each sprite and does not
        draw those with hidden True
        """

        if surface is None:
            surface = self.screen

        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        for s, r in spritedict.items():
            if not s.hidden:
                newrect = surface_blit(s.image, s.rect)
                if r == 0:
                    dirty_append(newrect)
                else:
                    dirty_append(newrect.union(r))
                spritedict[s] = newrect
            elif r:
                dirty_append(r)
        return dirty

    def move(self):
        levels = self.levels.keys()
        for l in levels:
            for sprite in self.levels[l].sprites():
                sprite.move()

    def pop(self):
        sprite = self.sprites()[0]
        self.remove(sprite)
        return sprite

    def kill(self):
        """Call the C{kill} method on every sprite in this group, to remove
        all of the sprites from all of the groups they are in.

        """

        for s in self.sprites():
            s.kill()

        levels = self.levels.values()
        levels.remove(self)
        for level in levels:
            level.kill()



class PSprite(Sprite):
    """
    New pygsear sprite class. Not used by any other code yet.
    """
    def __init__(self, window=None):
        Sprite.__init__(self)

        if window is None:
            if hasattr(conf, 'window'):
                window = conf.window
            else:
                window = Screen.Window()
        self.window = window

        self.rect = pygame.Rect((0, 0), (0, 0))
        self.rect_prev = pygame.Rect(self.rect)
        self.crect = self.rect

        self.image = 'None.png'
        self.hidden = 0

        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.gx = 0
        self.gy = 0

        self.rotation = 0
        self.direction = 0

    # Pass rect attributes through to self.rect
    def _get_top(self):
        return self.rect.top
    def _set_top(self, top):
        self.rect.top = top
    top = property(_get_top, _set_top)

    def _get_bottom(self):
        return self.rect.bottom
    def _set_bottom(self, bottom):
        self.rect.bottom = bottom
    bottom = property(_get_bottom, _set_bottom)

    def _get_left(self):
        return self.rect.left
    def _set_left(self, left):
        self.rect.left = left
    left = property(_get_left, _set_left)

    def _get_right(self):
        return self.rect.right
    def _set_right(self, right):
        self.rect.right = right
    right = property(_get_right, _set_right)

    def _get_topleft(self):
        return self.rect.topleft
    def _set_topleft(self, topleft):
        self.rect.topleft = topleft
    topleft = property(_get_topleft, _set_topleft)

    def _get_size(self):
        return self.rect.size
    def _set_size(self, size):
        self.rect.size = size
    size = property(_get_size, _set_size)

    def _get_center(self):
        return self.rect.center
    def _set_center(self, center):
        if center == 'center':
            center = self.window.rect.center
        self.rect.center = center
    center = property(_get_center, _set_center)

    def _get_centerx(self):
        return self.rect.centerx
    def _set_centerx(self, centerx):
        if centerx == 'center':
            centerx = self.window.rect.centerx
        self.rect.centerx = centerx
    centerx = property(_get_centerx, _set_centerx)

    def _get_centery(self):
        return self.rect.centery
    def _set_centery(self, centery):
        if centery == 'center':
            centery = self.window.rect.centery
        self.rect.centery = centery
    centery = property(_get_centery, _set_centery)


    # Other ways to access the self.rect
    def _get_position(self):
        return self.rect[0:2]
    def _set_position(self, position):
        if position == 'random':
            maxX = conf.WINWIDTH - self.rect.width
            maxY = conf.WINHEIGHT - self.rect.height
            position = (random.randrange(maxX+1), random.randrange(maxY+1))

        self.rect[0:2] = position
    position = property(_get_position, _set_position)


    # What the sprite looks like
    def _get_image(self):
        return self._image
    def _set_image(self, image):
        try:
            self.size = image.get_size()
        except AttributeError:
            image = Util.load_image(image)
            self.image = image
        else:
            self._image = image
    image = property(_get_image, _set_image)


    def draw(self):
        """Blit image to layer

        @return: Affected L{pygame.Rect} which can be passed to L{pygame.display.update}.

        """

        self.window.screen.blit(self.image, self.rect)
        return self.rect

    def udraw(self):
        """Draw image and update display.

        This function is almost exclusively for use in an interactive session,
        since it updates the screen immediately after drawing the sprite instead
        of waiting and updating after all sprites have been drawn.

        """

        rect = self.draw()
        pygame.display.update(rect)

    def clear(self):
        """Erase sprite to background

        @return: Affected L{pygame.Rect} which can be passed to
        L{pygame.display.update}.

        """

        self.window.screen.blit(self.window.bg, self.rect, self.rect)
        return self.rect

    # Motion
    def move(self):
        pass

    def _get_vx(self):
        return self.__vx
    def _set_vx(self, vx):
        self.__vx = vx
    vx = property(_get_vx, _set_vx)

    def _get_vy(self):
        return self.__vy
    def _set_vy(self, vy):
        self.__vy = vy
    vy = property(_get_vy, _set_vy)

    def _get_ax(self):
        return self.__ax
    def _set_ax(self, ax):
        self.__ax = ax
    ax = property(_get_ax, _set_ax)

    def _get_ay(self):
        return self.__ay
    def _set_ay(self, ay):
        self.__ay = ay
    ay = property(_get_ay, _set_ay)


    def distance(self, rect):
        """return the distance from the sprite to a point

        @param rect: Rect to find the distance to.

        """

        x, y = self.rect.topleft
        x1, y1 = rect.topleft

        return math.hypot((x1 - x), (y1 - y))

    def direction(self, rect):
        """return the direction from the sprite to a point

        @param rect: Rect to find the direction to.

        """

        x, y = self.rect.topleft
        x1, y1 = rect.topleft

        return math.atan2(-(y1 - y), (x1 - x))


    def onscreen(self, slack=None, **kw):
        """return True if image is on the screen or layer.

        If C{slack} is None, and keyword args are included for
        particular edges (ie C{top} or C{right}) checks I{only}
        the edges passed by keyword.

        @keyword left: Sprite can be this far from left edge.
        @keyword right: Sprite can be this far from right edge.
        @keyword top: Sprite can be this far from top edge.
        @keyword bottom: Sprite can be this far from bottom edge.
        @keyword clamp: Sprite will be moved completely onscreen.

        @param slack: Distance sprite can be off screen and still
            return True. Use a negative number to restrict the sprite
            to a smaller area.

        """

        if slack is None and len(kw) == 0:
            return self.window.rect.contains(self.rect)

        if kw.has_key('clamp'):
            if kw['clamp']:
                clamp = 1
            else:
                clamp = 0
        else:
            clamp = 0

        if slack is not None:
            left = slack
            right = slack
            top = slack
            bottom = slack
        else:
            left = None
            right = None
            top = None
            bottom = None

            if kw.has_key('left'):
                left = kw['left']
            if kw.has_key('right'):
                right = kw['right']
            if kw.has_key('top'):
                top = kw['top']
            if kw.has_key('bottom'):
                bottom = kw['bottom']

        off = 0
        if left is not None:
            if self.left < self.window.rect.left:
                off = 1

        if right is not None:
            if self.right < self.window.rect.right:
                off = 1

        if top is not None:
            if self.top < self.window.rect.top:
                off = 1

        if bottom is not None:
            if self.bottom < self.window.rect.bottom:
                off = 1

        if clamp:
            self.window.rect.clamp_ip(self.rect)

        return not off


    def pause(self):
        pass

    def unpause(self):
        pass


class Drawable(Sprite):
    """Things to draw on screen."""

    def __init__(self, w=None):
        """Initialize Drawable sprite.

        @param w: Layer on which sprite lives.

        """

        Sprite.__init__(self)
        if w is None:
            if hasattr(conf, 'window'):
                w = conf.window
            else:
                w = Screen.Window()
        self.window = w
        self.screen = w.screen
        self.bg = w.bg
        self.rect = pygame.Rect((0, 0), (0, 0))

        # self.position should always be the position.
        # This list should never be accessed directly
        # but always through get_position and set_position
        self.position = [0, 0]
        self.cx = 0 # distance from upper left to "center"
        self.cy = 0 # distance from upper left to "center"
        Drawable.set_position(self, (0, 0))
        self.set_path(Path.PathNG())

        self.set_crect()

        self.hidden = 0

    def draw(self, surface=None):
        """Blit image to layer

        @param surface: Pygame surface to draw to, or if None,
        will draw to the sprite's screen.

        @return: Affected L{pygame.Rect} which can be passed to L{pygame.display.update}.

        """

        if surface is None:
            self.screen.blit(self.image, self.rect)
        else:
            surface.blit(self.image, self.rect)
        return pygame.Rect(self.rect)

    def udraw(self, surface=None):
        """Draw image and update display.

        This function is almost exclusively for use in an interactive session,
        since it updates the screen immediately after drawing the sprite instead
        of waiting and updating after all sprites have been drawn.

        @param surface: L{pygame.Surface} to draw to, or if None,
        will draw to the sprite's screen.

        """

        self.draw(surface=surface)
        pygame.display.update(self.rect)
        #print 'rect', self.rect

    def clear(self, surface=None):
        """Erase sprite to background

        @param surface: L{pygame.Surface} to draw to, or if None,
        will draw to the sprite's screen.

        @return: Affected L{pygame.Rect} which can be passed to
        L{pygame.display.update}.

        """

        if surface is None:
            self.screen.blit(self.bg, self.rect, self.rect)
        else:
            surface.blit(self.bg, self.rect, self.rect)
        return pygame.Rect(self.rect)

    def uclear(self, surface=None):
        """clear sprite and update display

        @param surface: L{pygame.Surface} to draw to, or if None,
        will draw to the sprite's screen.

        """

        self.clear(surface=surface)
        pygame.display.update(self.rect)

    def _set_position(self, location):
        """Move sprite to location.

        @param location: Must be a 2-tuple C{(x, y)}

        """

        x, y = location
        self.position[0], self.position[1] = x, y
        self.rect[0] = x - self.cx
        self.rect[1] = y - self.cy
        self.set_crect()

    def set_position(self, location, *args):
        """Move sprite to location.

        set_position can be called as either C{set_position(x, y)} or as
        C{set_position((x, y))} which makes it a bit easier to use from
        an interactive session.

        The extra checks for whether the argument is a single 2-tuple or
        2 separate numbers does make the function run a bit slower, so if
        speed is an issue, you should call L{Drawable._set_position}.

        @param location: can be a single 2-tuple C{(x, y)}, or 2 numbers

        """

        lenargs = len(args)
        if lenargs > 1:
            raise TypeError, "set_position takes either a 2-tuple of numbers, or 2 numbers"
        try:
            x, y = location
        except TypeError:
            x, y = location, args[0]
        else:
            if lenargs > 1:
                raise TypeError, "set_position takes either a 2-tuple of numbers, or 2 numbers"
        self._set_position((x, y))

    def get_position(self):
        """return a copy of the sprite's position"""

        return self.position[:]

    def distance(self, point):
        """return the distance from the sprite to a point

        @param point: Point to find the distance to.

        """

        x, y = self.get_position()
        x1, y1 = point

        return math.hypot((x1 - x), (y1 - y))

    def direction(self, point):
        """return the direction from the sprite to a point

        @param point: Point to find the direction to.

        """

        x, y = self.get_position()
        x1, y1 = point

        return math.atan2(-(y1 - y), (x1 - x))

    def set_positionRandom(self, slack=0):
        """Move sprite to a random location on screen

        @param slack: If this is included, the sprite will be more or
            less constrained to the screen. Use negative numbers to restrict
            the sprite to a smaller area, positive numbers to allow the
            sprite to actually be offscreen.

        """

        sx, sy = self.get_size()
        minX = -slack
        minY = -slack
        maxX = conf.WINWIDTH - sx - slack
        maxY = conf.WINHEIGHT - sy - slack

        x = random.randrange(minX, maxX+1)
        y = random.randrange(minY, maxY+1)

        self._set_position((x, y))

    def center(self, x=None, y=None, dx=None, dy=None):
        """Align the Drawable in its layer

        If no parameters are included, the sprite will be moved
        to the center of its screen layer, or use the parameters
        to adjust where exactly the sprite should be placed.

        @param x: offset from left edge
            if negative, offset from right edge
        @param y: offset from top edge
            if negative, offset from bottom edge
        @param dx: horizontal offset from center
        @param dy: vertical offset from center

        @raises TypeError: Caller may include either the C{x} parameter
            to align the sprite from the edge of the screen, or the C{dx}
            parameter to align the sprite from the center of the screen,
            but not both.
        @raises TypeError: Caller may include either the C{y} parameter
            to align the sprite from the edge of the screen, or the C{dy}
            parameter to align the sprite from the center of the screen,
            but not both.

        """

        if y is not None and dy is not None:
            raise TypeError, "Must use only y or dy"
        if x is not None and dx is not None:
            raise TypeError, "Must use only x or dx"

        w, h = self.get_size()
        #print 'center', x, y, w, h

        w_layer, h_layer = self.screen.get_size()
        #print 'wwh', w_layer, h_layer

        if x is None and dx is None:
            x = (w_layer - w) / 2
        elif x is None:
            x = ((w_layer - w) / 2) + dx
        elif x < 0:
            x = w_layer - w + x

        if y is None and dy is None:
            y = (h_layer - h) / 2
        elif y is None:
            y = ((h_layer - h) / 2) + dy
        elif y < 0:
            y = h_layer - h + y

        #print self, 'cxy', x, y, x + self.cx, y + self.cy
        self._set_position((x+self.cx, y+self.cy))

    def nudge(self, dx=0, dy=0):
        """Move sprite.

        @param dx: Distance to move in x-direction.
        @param dy: Distance to move in y-direction.

        """

        x, y = self.get_position()
        x += dx
        y += dy
        self.set_position((x, y))

    def set_size(self, size):
        """Set size of sprite's rect.

        @param size: C{(width, height)}

        """

        x, y = size
        self.rect[2] = x
        self.rect[3] = y

    def get_size(self):
        """return size of sprite's rect.

        @return: L{pygame.Rect}

        """

        return (self.rect[2], self.rect[3])

    def stretch(self, dx=None, dy=None, size=None, keepAspectRatio=1):
        """Change the size of sprite's image, and rect.

        @param dx: Number of pixels to stretch in the x direction (can be neg)
        @param dy: Number of pixels to stretch in the y direction (can be neg)
        @param size: Tuple with new overall size C{(width, height)}
        @param keepAspectRatio: If True, the new image will be padded
            with transparent borders.

        """

        if not hasattr(self, 'original_image'):
            # All stretch operations start from the original image, so that
            # the image will not get completely distorted after a few stretches.
            image = self.image
            self.original_image = image
        else:
            image = self.original_image

        if size is None and dx is None and dy is None:
            raise TypeError, "must specify size or dx/dy"
        elif size is None:
            w, h = self.get_size()
            if keepAspectRatio:
                if dx is None:
                    dx = w * float(dy) / h
                if dy is None:
                    dy = h * float(dx) / w
            w += (dx or 0)
            h += (dy or 0)
        else:
            w, h = size

        new_image = scale_image(image, w, h, keepAspectRatio)
        self.image = new_image
        self.rect.size = (w, h)



    def onscreen(self, slack=None, **kw):
        """return True if image is on the screen or layer.

        If C{slack} is None, and keyword args are included for
        particular edges (ie C{top} or C{right}) checks I{only}
        the edges passed by keyword.

            - param left: Sprite can be this far from left edge.
            - param right: Sprite can be this far from right edge.
            - param top: Sprite can be this far from top edge.
            - param bottom: Sprite can be this far from bottom edge.

            - param layer: Use this layer instead of the sprite's
                screen layer.

        @param slack: Distance sprite can be off screen and still
            return True. Use a negative number to restrict the sprite
            to a smaller area.

        """

        if not kw.has_key('layer'):
            layerrect = self.window.rect
        else:
            layerrect = kw['layer'].rect
            del(kw['layer'])

        if slack is None and len(kw) == 0:
            return layerrect.contains(self.rect)
        else:
            sx, sy = layerrect.size

        x, y = self.get_position()
        w, h = self.get_size()

        if kw.has_key('jail'):
            if kw['jail']:
                jail = 1
            else:
                jail = 0
        else:
            jail = 0

        if slack is not None:
            left = slack
            right = slack
            top = slack
            bottom = slack
        else:
            left = None
            right = None
            top = None
            bottom = None

            if kw.has_key('left'):
                left = kw['left']
            if kw.has_key('right'):
                right = kw['right']
            if kw.has_key('top'):
                top = kw['top']
            if kw.has_key('bottom'):
                bottom = kw['bottom']

        off = 0
        if left is not None:
            minX = -left
            if x < minX:
                x = minX
                off = 1

        if right is not None:
            maxX = sx - w + right
            if x > maxX:
                x = maxX
                off = 1

        if top is not None:
            minY = -top
            if y < minY:
                y = minY
                off = 1

        if bottom is not None:
            maxY = sy - h + bottom
            if y > maxY:
                y = maxY
                off = 1

        if jail:
            self._set_position((x, y))

        return not off

    def solid(self, other, move_both=0):
        """move sprite so that it does not overlap with other sprite

        @param other: other sprite
        @param move_both: if set, move both sprites in the effort to get them
            apart, otherwise only move the original sprite.

        """

        if self.collide(other):
            self._set_position(self.path.positionOld)
            if move_both:
                other._set_position(other.path.positionOld)

        sx, sy = self.crect.center
        ox, oy = other.crect.center

        #print 'before', sx, sy, scx, scy, ox, oy, ocx, ocy
        while self.collide(other):
            if sx < ox:
                sx -= 1
            elif sx > ox:
                sx += 1

            if sy < oy:
                sy -= 1
            elif sy > oy:
                sy += 1

            if move_both:
                if sx < ox:
                    ox += 1
                elif sx > ox:
                    ox -= 1

                if sy < oy:
                    oy += 1
                elif sy > oy:
                    oy -= 1

            self._set_position((sx, sy))
            self.set_crect()

            if move_both:
                other._set_position((ox, oy))
                other.set_crect()

        #print 'after ', sx, sy, scx, scy, ox, oy, ocx, ocy

    def set_crect(self, crect=None):
        """set the collision L{pygame.Rect} used for collision checking.

        @param crect: rect to use for collision checking.
            crect gets centered on the rect.
            If None, use the rect as the crect also.

        """

        if crect is None:
            if hasattr(self, 'crect'):
                self.crect.center = self.rect.center
            else:
                self.crect = pygame.Rect(self.rect)
        else:
            self.crect = pygame.Rect(crect)
            self.crect.center = self.rect.center

    def collide(self, other):
        """return True if this sprite and other sprite overlap.

        Uses the C{.crect} attribute of each sprite to check for
        a collision (overlap).

        @param other: The other sprite to check for collision.

        @returns: True if the sprites overlap.
        @rtype: C{bool}

        """

        return self.crect.colliderect(other.crect)

    def collidelist(self, lothers):
        """return True if this sprite and any in list of others collide.

        The True value is the other sprite. Note that more than one sprite in
        the list may be colliding with the sprite, but only one is returned.

        @param lothers: List of other sprites to check for collision.

        @returns: Other sprite if there is a collision, or C{False}.
        @rtype: C{Drawable} or C{False}

        """

        rects = [o.crect for o in lothers]

        index = self.crect.collidelist(rects)
        if index == -1:
            return 0
        else:
            return lothers[index]

    def collidelistall(self, lothers):
        """return True if this sprite and any in list of others collide.

        The True value is the list of colliding sprites, or if there is no
        collision, an empty sequence.

        @param lothers: List of other sprites to check for collision.

        @returns: List of colliding sprites, or empty list.
        @rtype: C{List}

        """

        rects = [o.crect for o in lothers]

        indexes = self.crect.collidelistall(rects)
        if not indexes:
            return []
        else:
            return [lothers[index] for index in indexes]

    def set_path(self, path):
        """set which path to follow

        path: Instance of L{Path.Path}.

        """

        self.path = path
        position = path.get_position()
        path.position = self.position
        self._set_position(position)
        Drawable.move(self)

    def runPath(self, frames=0):
        """call move() continuously

        @param frames: Number of times to call move(), or
            if frames is 0, call move() until C{EndOfPath}.

        """

        self.path.reset()
        count = 0
        #bg = self.bg
        clock = pygame.time.Clock()
        while count < frames or not frames:
            conf.ticks = clock.tick(conf.MAX_FPS)
            dirty = [self.clear()]
            try:
                self.move()
            except Path.EndOfPath:
                self.path.reset()
                raise
            dirty.append(self.draw())
            pygame.display.update(dirty)
            count += 1

    def move(self):
        """set position to next position on path"""

        try:
            self._set_position(self.path.next())
        except StopIteration:
            raise Path.EndOfPath

    def pause(self):
        """stop moving along Path"""

        self.path.pause()

    def unpause(self):
        """start moving along Path"""

        self.path.unpause()

    def can_see(self, target, blocking_rects_list):
        """Performs a los (line of sight) check from the center of the
        source to the center of the target. Adapted from the Pygame Code
        Repository (PCR).

        Makes the following assumption:

            1.  Both the source and target include a L{pygame.Rect}
                attribute called C{crect}.

        @param target: Sprite to check for visibility.
        @param blocking_rects_list: List of L{pygame.Rect}s which can block
            the visibility.

        @returns: True if line of sight is clear, or False if it is blocked.
        @rtype: bool

        """

        los_line_p1 = self.crect.center
        los_line_p2 = target.crect.center


        # check each candidate rect against this los line. If any of them
        # intersect, the los is blocked.

        for rect in blocking_rects_list:
            block_p1 = rect.topleft
            block_p2 = rect.bottomright
            if line_seg_intersect(los_line_p1, los_line_p2, block_p1, block_p2):
                return 0
            block_p1 = rect.topright
            block_p2 = rect.bottomleft
            if line_seg_intersect(los_line_p1, los_line_p2, block_p1, block_p2):
                return 0
        return 1

class Layer(Drawable, Screen.Layer):
    """Screen that can be used as a sprite"""

    def __init__(self, w=None, size=None, color=TRANSPARENT):
        Drawable.__init__(self, w)
        self._window = self.window
        if size is None:
            size = self.window.screen.get_size()
        Screen.Layer.__init__(self, size)
        self.image = self._fg
        self.screen = self._fg
        self.screen.fill(color)
        self.bg = self._bg
        self.bg.fill(color)

        if color == TRANSPARENT:
            self.image.set_colorkey(color)
            self.bg.set_colorkey(color)

        self.sprites = SpriteGroup(layer=self)

    def updateContents(self):
        """move and re-draw all the sprites that use this layer"""

        self.sprites.clear()
        self.sprites.move()
        dirty = self.sprites.draw()
        #self.update(dirty)

    def draw(self, surface=None):
        """draw image, returning affected rect"""

        rect = self.rect
        if surface is None:
            self._window.screen.blit(self.image, rect)
        else:
            surface.blit(self.image, rect)
        return pygame.Rect(rect)

    def clear(self, surface=None):
        """erase image to background, returning affected rect"""

        if surface is None:
            self._window.screen.blit(self._window.bg, self.rect, self.rect)
        else:
            surface.blit(self._window.bg, self.rect, self.rect)
        return pygame.Rect(self.rect)

    def center(self, x=None, y=None, dx=None, dy=None):
        """center the Drawable in its layer

        @param x: offset from left edge or
            if negative, offset from right edge
        @param y: offset from top edge or
            if negative, offset from bottom edge
        @param dx: horizontal offset from center
        @param dy: vertical offset from center

        """

        if y is not None and dy is not None:
            raise TypeError, "Must use only y or dy"
        if x is not None and dx is not None:
            raise TypeError, "Must use only x or dx"

        w, h = self.get_size()
        w_layer, h_layer = self._window.screen.get_size()

        if x is None and dx is None:
            x = (w_layer - w) / 2
        elif x is None:
            x = ((w_layer - w) / 2) + dx
        elif x < 0:
            x = w_layer - w + x

        if y is None and dy is None:
            y = (h_layer - h) / 2
        elif y is None:
            y = ((h_layer - h) / 2) + dy
        elif y < 0:
            y = h_layer - h + y

        self._set_position((x, y))


class Shape(Drawable):
    """Simple geometric shapes."""

    def __init__(self, w=None):
        Drawable.__init__(self, w)

    def paint(self):
        """Change the color of the shape."""

        raise NotImplementedError

    def set_color(self, color=None, r=None, g=None, b=None):
        """Set the color for drawing.

        The caller can choose one of a few ways to set the color:
            - an RGB tuple can be passed in as the C{color} parameter
                (or as the first argument)
            - one or more of C{r}, C{g}, and C{b} parameters can (also) be
                passed as that portion of the color tuple.

                If these are given in addition to the C{color} parameter,
                these will override the elements in the C{color} tuple.
                I{ie. C{set_color((10, 10, 10), r=50)} will set the color
                to C{(50, 10, 10)}}

                If these are given with NO color tuple passed, the resulting
                color will start with the current color, with the new elements
                being set from the passed parameters I{ie, if the color is
                C{(100, 100, 100)} before the call, calling
                C{set_color(g=50, b=50)} will set the color to C{(100, 50, 50)}}

            - if no parameters are passed at all, the color is set to WHITE.

        @param color: an RGB tuple, or the word 'random' which will choose
            a color at random from (not quite) all possible.
        @param r: The red value of the color (0 - 255)
        @param g: The green value of the color (0 - 255)
        @param b: The blue value of the color (0 - 255)

        """

        if color is None and r is None and g is None and b is None:
            # WHITE
            rr = 255
            rg = 255
            rb = 255
        elif color is None:
            rr, rg, rb = self.color
        elif color == 'random':
            rr = random.randint(50, 250)
            rg = random.randint(50, 250)
            rb = random.randint(50, 250)
        elif color:
            rr, rg, rb = color[:3]

        if r is not None:
            rr = r
        if g is not None:
            rg = g
        if b is not None:
            rb = b

        color = (rr, rg, rb)
        self.color = color

        self.paint()


class Rectangle(Shape):
    """Rectangle, aligned with no rotation

    position measured from top left corner.

    """

    def __init__(self, w=None, width=20, height=10, color=WHITE):
        Shape.__init__(self, w)
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height)).convert()
        self.set_color(color)
        self.rect = pygame.Rect((0, 0), (width, height))
        self.set_position((0, 0))
        self.set_crect(self.rect)
        #self.cx, self.cy = width/2.0, height/2.0

    def paint(self):
        """Change the color of the shape."""

        self.image.fill(self.color)

    def border(self, width=10, color=WHITE,
                    left=None, right=None, top=None, bottom=None):
        """Draw a border around the rectangle

        @param width: pixel width of border
        if only width is passed, an equal width border will be
        drawn around the entire rectangle.

        @param color: color of border

        @param left: left-side border
        @param right: right-side border
        @param top: top-side border
        @param bottom: bottom-side border
        each border width can be specified, or if not specified, will
        default to using width. Specify width of 0 for no border on
        a particular side.

        """

        image = self.image

        w, h = image.get_size()

        if left is None:
            left = width
        if right is None:
            right = width
        if top is None:
            top = width
        if bottom is None:
            bottom = width

        if left:
            pygame.draw.rect(image, color, (0, 0, left, h))
        if right:
            pygame.draw.rect(image, color, (w-right, 0, w, h))
        if top:
            pygame.draw.rect(image, color, (0, 0, w, top))
        if bottom:
            pygame.draw.rect(image, color, (0, h-bottom, w, h))


class Square(Rectangle):
    """Square, aligned with no rotation.

    position measured from top left corner.

    """

    def __init__(self, w=None, side=10, color=WHITE):
        Rectangle.__init__(self, w, side, side, color)


class Circle(Shape):
    """Circle.

    position measured from top left corner of enclosing square.

    """

    def __init__(self, w=None, radius=10, color=WHITE, bgcolor=TRANSPARENT):
        Shape.__init__(self, w)
        self.radius = radius
        self.width = 2 * radius
        self.height = 2 * radius
        self.image = pygame.Surface((self.width, self.height)).convert()
        self.image.fill(bgcolor)
        self.image.set_colorkey(bgcolor)
        self.set_color(color)
        self.rect = pygame.Rect((0, 0), (self.width, self.height))
        self.set_position((0, 0))
        self.set_crect(self.rect)

    def paint(self):
        radius = self.radius
        pygame.draw.circle(self.image, self.color, (radius, radius), radius, 0)


class Image(Drawable):
    """Static sprite from image in a file"""
    filename = None

    def __init__(self, w=None, filename=None, image=None,
                    colorkey=TRANSPARENT, alpha=0, convert=1):
        """Create sprite from file or surface

        @param w: L{Screen.Layer} to draw in.
        @param filename: Name of file to load image from.
        @param image: L{pygame.Surface} to use as image.
        @param colorkey: RGB tuple for transparent areas.
        @param alpha: Set True if sprite should use alpha blending.
        @param convert: Set true if image should be optimized.

        """

        Drawable.__init__(self, w)

        if filename is None and image is None:
            if self.filename is None:
                self.image = load_image('None.png', convert=convert)
            else:
                self.image = load_image(self.filename, convert=convert)
        elif image is None:
            self.image = load_image(filename, convert=convert)
        else:
            self.image = image

        if colorkey is not None:
            self.image.set_colorkey(colorkey)
            if not alpha:
                self.image.convert()

        if alpha:
            self.image.set_alpha(alpha, pygame.locals.RLEACCEL)
            self.image.convert_alpha()

        self.rect = self.image.get_rect()
        self.set_position((0, 0))
        self.set_crect(self.rect)


class AnimatedImage(Drawable):
    """Animated sprite using multiple images"""
    filenames = None
    dirname = None

    def __init__(self, w=None, filenames=None, dirname=None, flipticks=250, colorkey=TRANSPARENT):
        """Load multiple ordered images from multiple files.

        By default, each call to move() flips to next image.

        @param w: L{Screen.Layer} to draw in.
        @param filenames: list of files to load
            if files is a string instead of a list of files,
            use the string as the name of a directory from
            which to load all files as images. Sort alpha
            by file name for ordering.
        @param flipticks: number of ticks to wait between flips

        """

        if filenames is None and dirname is None:
            if self.filenames is not None:
                filenames = self.filenames
            elif self.dirname is not None:
                dirname = self.dirname
            else:
                raise TypeError, "Must give filenames or dirname"

        self.flipticks = flipticks
        self.ticks = flipticks
        self.images = load_images(filenames, dirname)

        for image in self.images:
            image.set_colorkey(colorkey)

        self.imageNum = 0
        Drawable.__init__(self, w)
        self.flip()
        self.set_position((0, 0))
        self.set_crect(self.rect)

    def flip(self):
        """switch to next image in sequence"""

        self.image = self.images[self.imageNum]
        self.imageNum += 1
        if self.imageNum >= len(self.images):
            self.imageNum = 0
        self.set_size(self.image.get_size())
        self.set_crect()

    def move(self):
        """set position to next position on path and flip to next image"""

        self.ticks -= conf.ticks
        if self.ticks < 0:
            self.flip()
            self.ticks += self.flipticks

        Drawable.move(self)


class MultiImage(Drawable):
    """Multiple images from multiple files."""
    filenames = None

    def __init__(self, w=None, filenames=None, dirname=None, defaultImage=None,
                    colorkey=TRANSPARENT, convert=1):
        """Load multiple images from multiple files

        Images get stored in a dict for retrieval by name.

        @param w: L{Screen.Layer} to draw in.
        @param filenames: List of image file names to load.
        @param dirname: Name of directory from which to load all images.
        @param defaultImage: Name of the default image.
        @param colorkey: RGB tuple to use for transparency.
        @param convert: If True, call convert() for all images.

        """

        if filenames is None and dirname is None:
            filenames = self.filenames

        Drawable.__init__(self, w)
        self.images = Util.load_images_dict(filenames, dirname)
        self.defaultImage = defaultImage

        for filename in self.images.keys():
            image = self.images[filename]
            self.addImage(filename, image, colorkey, convert)

        if not self.images:
            image = Util.load_image('None.png')
            self.addImage('None.png', image, colorkey, convert=1)
            self.defaultImage = 'None.png'
        else:
            self.defaultImage = self.images.keys()[0]

        self.image = self.images[self.defaultImage]
        self.set_position((0, 0))
        self.set_size(self.image.get_size())
        self.set_crect(self.rect)

    def addImage(self, filename='default', image=None, colorkey=TRANSPARENT, convert=1):
        """add image to list of available images

        @param filename: string file name from which to load image
            If image is not None, file is used as the
            name (key) to access the image.
        @param image: image (Surface) to add

        """

        if image is None:
            image = load_image(filename, convert)

        if colorkey is not None:
            image.set_colorkey(colorkey)

        self.images[filename] = image
        if self.defaultImage == 'None.png':
            self.removeImage('None.png')
            self.defaultImage = filename

    def removeImage(self, key):
        """remove image by name"""

        del(self.images[key])

    def flip(self, imageName='default'):
        """switch image by name

        @param imageName: string with name of image (without file type suffix)

        """

        self.image = self.images[imageName]
        self.set_size(self.image.get_size())
        self.set_crect()

    def stretch(self, dx=None, dy=None, size=None, keepAspectRatio=1):
        """Change the size of sprite's image, and rect.

        @param dx: Number of pixels to stretch in the x direction (can be neg)
        @param dy: Number of pixels to stretch in the y direction (can be neg)
        @param size: Tuple with new overall size C{(width, height)}
        @param keepAspectRatio: If True, the new image will be padded
            with transparent borders.

        """

        if not hasattr(self, 'original_images'):
            # All stretch operations start from the original image, so that
            # the image will not get completely distorted after a few stretches.
            images = self.images
            self.original_images = images
        else:
            images = self.original_images

        if size is None and dx is None and dy is None:
            raise TypeError, "must specify size or dx/dy"
        elif size is None:
            w, h = self.get_size()
            if keepAspectRatio:
                if dx is None:
                    dx = w * float(dy) / h
                if dy is None:
                    dy = h * float(dx) / w
            w += (dx or 0)
            h += (dy or 0)
        else:
            w, h = size

        for imagename, image in images.items():
            new_image = scale_image(image, w, h, keepAspectRatio)
            self.images[imagename] = new_image

        self.rect.size = (w, h)


class RotatedImage(MultiImage):
    """Sprite with auto-generated rotated images"""

    def __init__(self, w=None, filename=None, steps=4, image=None,
                    colorkey=TRANSPARENT, convert=1, cx=None, cy=None):
        """Initialize RotatedImage

        @param w: L{Screen.Layer} to draw in.
        @param filename: name of file from which to load image
        @param steps: number of separate rotated images to create
            I{B{Note} -- does not work with > 360 steps}
        @param image: image to use, instead of loading from file
        @param colorkey: set this colorkey on all rotated images
        @param convert: boolean, 1 = convert() every rotated image
        @param cx: x-coordinate of center of rotation relative to the
            upper left corner of the image.
        @param cy: y-coordinate of center of rotation relative to the
            upper left corner of the image.

        """

        MultiImage.__init__(self, w=w, colorkey=colorkey, convert=convert)
        if image is None and filename is None:
            raise TypeError, 'Must include filename or image'
        elif image is not None:
            self.addImage(filename='image', image=image,
                                colorkey=colorkey, convert=convert)
        if image is None:
            self.addImage(filename, colorkey=colorkey, convert=convert)

        self.set_rotation(0)
        self.set_rotationRate(0)

        name, image = self.images.items()[0]
        if cx is not None or cy is not None:
            # deal with offset center of rotation
            w, h = image.get_size()
            #print 'wh', w, h

            if cx is None:
                cx = w / 2.0
            if cy is None:
                cy = h / 2.0

            if cx > w:
                wnew = 2 * cx
                x = 0
            elif cx < 0:
                wnew = (2 * w) + (2 * abs(cx))
                x = w + (2 * -cx)
            else:
                wnew = (2 * w) - (2 * cx)
                x = w - (2 * cx)

            if cy > h:
                hnew = 2 * cy
                y = 0
            elif cy < 0:
                hnew = (2 * h) + (2 * abs(cy))
                y = h + (2 * -cy)
            else:
                hnew = (2 * h) - (2 * cy)
                y = h - (2 * cy)

            wnew = int(wnew)
            hnew = int(hnew)

            i = pygame.Surface((wnew, hnew))
            i.fill(colorkey)
            i.blit(image, (x, y))
            i.set_colorkey(colorkey)
            image = i

        degPerStep = 360 / steps
        for step in range(steps):
            deg = step * degPerStep
            s = pygame.transform.rotate(image, deg)
            s.set_colorkey(colorkey)
            if convert:
                s.convert()
            self.images[int(deg)] = s
        self.removeImage(name)

        self.keys = list(self.images.keys())
        self.keys.sort()

        self.flip(0)
        self.set_crect(self.image.get_rect())

    def rotate(self, rad=None):
        """rotate to the left by radians"""

        direction = self.get_rotation()
        self.set_rotation(direction + rad)

    def set_rotation(self, direction=None):
        """set angle of rotation

        @param direction: angle to set
        0 is pointing to the right
        positive is counter-clockwise

        """

        if direction is None:
            direction = self.path.get_direction()
        self.rotation = direction % PIx2 % PIx2

    def get_rotation(self):
        """return angle of rotation"""

        return self.rotation

    def set_rotationRate(self, rate):
        """set rate of rotation in radians / second"""

        self.rotationRate = rate

    def rotate_right(self):
        """set rotation rate to -2"""

        self.set_rotationRate(-2)

    def rotate_left(self):
        """set rotation rate to +2"""

        self.set_rotationRate(2)

    def rotate_stop(self):
        """set rotation rate to 0"""

        self.set_rotationRate(0)

    def rotate_towards(self, point):
        """turn as quickly as possible towards a point"""

        direction = self.direction(point)
        rotation = self.get_rotation()

        rad = (rotation - direction) % PIx2

        if rad > PI:
            rad -= PIx2
        elif rad < -PI:
            rad += PIx2

        if rad > 0.1:
            self.rotate_right()
        elif rad < -0.1:
            self.rotate_left()
        else:
            self.rotate_stop()

    def flip(self, key=None):
        """Switch images for the sprite"""

        if key is not None:
            self.key = key
        else:
            self.key += 1
        lenkeys = len(self.keys)
        if self.key >= lenkeys:
            self.key = 0
        self.set_image(self.key)
        self.set_position(self.get_position())
        self.set_rotation((self.key / lenkeys) * PIx2)

    def set_closest(self):
        """flip to the image for the current direction"""

        direction = self.get_rotation()
        i = int((direction / PIx2) * len(self.images))
        self.set_image(i)
        self.set_position(self.get_position())

    def set_image(self, key):
        """Change which image is being shown.

        @param key: dict key referencing the image to use.
            The keys are the rotation of the images.

        """

        deg = self.keys[key]
        self.image = self.images[deg]
        size = self.image.get_size()
        self.set_size(size)
        w, h = size
        self.cx, self.cy = (w / 2.0), (h / 2.0)
        self.set_crect()
        #print self.crect, id(self.crect)

    def move(self):
        if self.rotationRate:
            ticks = conf.ticks
            self.rotate(self.rotationRate * ticks/1000.0)

        self.set_closest()

        MultiImage.move(self)

class MultiRotated(RotatedImage):
    """Sprite with multiple auto-generated rotated images"""

    def __init__(self, w=None, filenames=None, steps=4,
                    colorkey=TRANSPARENT, convert=1, cx=None, cy=None):
        """Initialize MultiRotated

        @param w: L{Screen.Layer} to draw in.
        @param filenames: list of names of files from which to load images
        @param steps: number of separate rotated images to create for each
            image in C{filenames} I{B{Note} -- does not work with > 360 steps}
        @param colorkey: set this colorkey on all rotated images
        @param convert: boolean, 1 = convert() every rotated image
        @param cx: x-coordinate of center of rotation relative to the
            upper left corner of the image.
        @param cy: y-coordinate of center of rotation relative to the
            upper left corner of the image.

        """


        RotatedImage.__init__(self, w=w, filename=filenames[0], steps=steps,
                            colorkey=colorkey, convert=convert, cx=cx, cy=cy)
        self._images = {}

        for f in filenames:
            ri = RotatedImage(w=w, filename=f, steps=steps,
                    colorkey=colorkey, convert=convert, cx=cx, cy=cy)
            self._images[f] = ri

        self._images_keys = list(filenames)
        self._images_keys.sort()
        #print 'keys', self._images_keys
        self._images_key_idx = 0

        self.switch_images(filenames[0])
        self.set_flip_images_rate(0)
        self.flip_images_ticks = 0
        self.reset_flip_images()

    def set_flip_images_rate(self, rate):
        """Used to animate the images automatically.

        @param rate: number of times per second to switch to next image.

        """

        self.flip_images_rate = rate # switches per second

    def reset_flip_images(self):
        """Flip back to the first image in the series and reset counter."""

        if self.flip_images_rate:
            self.flip_images_ticks = 1000 / self.flip_images_rate
            self.flip_images_ticks_orig = self.flip_images_ticks

    def switch_images(self, f):
        """Change which set of images is being shown.

        @param f: filename of original image.

        """

        self.keys = self._images[f].keys
        self.images = self._images[f].images

    def flip_images(self):
        """flip to the next set of images."""

        idx = self._images_key_idx
        idx += 1
        if idx >= len(self._images):
            idx = 0
        key = self._images_keys[idx]
        #print idx, key
        self.keys = self._images[key].keys
        self.images = self._images[key].images
        self._images_key_idx = idx

    def move(self):
        if self.flip_images_rate:
            self.flip_images_ticks -= conf.ticks
            if self.flip_images_ticks < 0:
                self.flip_images()
                self.reset_flip_images()

        RotatedImage.move(self)


class String(Drawable):
    """A string of numbers, letters, or other characters."""

    def __init__(self, w=None, message="string", fontSize=20,
                    color=WHITE, bgcolor=TRANSPARENT):
        """Initialize the string sprite.

        @param w: L{Screen.Layer} to draw in.
        @param message: String to display.
        @param fontSize: Size of font to use.
        @param color: Foreground (text) color.
        @param bgcolor: Background color.

        """

        Drawable.__init__(self, w)
        self.message = str(message)

        self.fontSize = fontSize
        font = pygame.font.Font(None, fontSize)

        if self.message == '':
            size = font.size('test for size')
            w, h = size
            self.image = pygame.Surface((0, h))
        else:
            size = font.size(self.message)
            self.image = font.render(self.message, 1, color, bgcolor)

        if bgcolor == TRANSPARENT:
            self.image.set_colorkey(TRANSPARENT)
        self.rect = pygame.Rect((0, 0), size)
        self.set_crect(self.rect)


class Multi(Drawable, pygame.sprite.RenderUpdates):
    """Made up of a group of sprites.

    Create other Drawable instances, then addSprite() them in.

    xOffset - x distance from left side of group base position.
    yOffset - y distance from top side of group base position.

    """

    def __init__(self, w=None):
        Sprite.__init__(self)
        AbstractGroup.__init__(self)
        Drawable.__init__(self, w)
        self.image = pygame.surface.Surface((0,0))
        self.rect = self.image.get_rect()
        self.set_crect(self.rect)

    def sprites(self):
        """return all of the sprites in the group (including self, since
        the group is itself a sprite).

        """
        s = pygame.sprite.RenderUpdates.sprites(self)
        s.append(self)
        return s

    def innerSprites(self):
        """return all of the sprites in the group, except self.

        """

        s = pygame.sprite.RenderUpdates.sprites(self)
        if self in s:
            s.remove(self)

        return s

    def add(self, group):
        """Add this sprite to a group. NOT add a sprite to this group!

        @param group: Sprite Group to add this sprite to.

        """

        Drawable.add(self, group)
        for sprite in self.innerSprites():
            sprite.add(group)

    def add_internal(self, group):
        """add this sprite to a group"""
        Sprite.add_internal(self, group)
        RenderUpdates.add_internal(self, self)
        for s in self.innerSprites():
            group.add(s)

    def remove_internal(self, group):
        try:
            Sprite.remove_internal(self, group)
        except KeyError:
            pass

    def fix_neg_offsets(self, xo, yo):
        """try to correct for use of negative offset values when using addSprite.

        This is not working yet, and is not in use.

        """

        if xo < 0:
            xo = -xo
        else:
            xo = 0

        if yo < 0:
            yo = -yo
        else:
            yo = 0

        self.nudge(dx=-xo, dy=-yo)

        for sprite in self.innerSprites():
            sprite.path.xOffset += xo
            sprite.path.yOffset += yo

    def addSprite(self, sprite, xOffset=0, yOffset=0):
        """Add a sprite to this group.

        Note: does not work with negative offsets.

        @param sprite: sprite to add to this group.
        @param xOffset: x-distance from center sprite is displaced.
        @param yOffset: y-distance from center sprite is displaced.

        """

        if not hasattr(sprite, 'innerSprites'):
            self.spritedict[sprite] = 0
            sprite.add_internal(self)
            sprite.set_path(Path.Offset_path(self.path, xOffset, yOffset))

        else:
            self.spritedict[sprite] = 0
            sprite.path = Path.Offset_path(self.path, xOffset, yOffset)
            for s in sprite.innerSprites():
                self.spritedict[s] = 0
            sprite.move()

        rect = self.rect
        if rect.w == 0 and rect.h == 0:
            self.rect = pygame.Rect(sprite.rect)
        else:
            self.rect.union_ip(sprite.rect)

    def removeSprite(self, sprite):
        """Remove a sprite from this group.

        @param sprite: Sprite to remove.

        """
        del self.spritedict[sprite]

        self.rect = self.image.get_rect()
        for sprite in self.innerSprites():
            self.rect.union_ip(sprite.rect)

    def empty(self):
        for sprite in self.innerSprites():
            self.removeSprite(sprite)

    def kill(self):
        for sprite in self.innerSprites():
            sprite.kill()
        Sprite.kill(self)

    def draw(self):
        """Draw all of the sprites in the group.

        @returns: L{pygame.Rect} which can be passed to L{pygame.display.update}

        """

        dirty = pygame.sprite.RenderUpdates.draw(self, self.screen)
        return dirty

    def udraw(self):
        """Draw all of the sprites in the group and update the screen."""

        dirty = self.draw()
        pygame.display.update(dirty)

    def clear(self):
        """Erase all sprites in group to background

        This does not return the affected L{pygame.Rect}.

        """

        pygame.sprite.RenderUpdates.clear(self, self.screen, self.bg)

    def uclear(self):
        """Erase all of the sprites in the group and update the screen."""

        self.clear()
        pygame.display.update()

    def set_position(self, location, *args):
        """Move sprite to location, and all contained sprites to their
        relative offsets from location.

        @param location: Either a 2-tuple C{(x, y)} or 2 numbers.

        """

        if not args:
            Drawable.set_position(self, location)
        else:
            Drawable.set_position(self, location, args[0])

        for sprite in self.innerSprites():
            sprite.move()

    def _set_position(self, location):
        """Move sprite to location.

        @param location: Must be a 2-tuple C{(x, y)}

        """

        Drawable._set_position(self, location)
        for sprite in self.innerSprites():
            sprite.move()

    def set_path(self, path):
        """Set path for sprite to follow.

        @param path: L{Path.Path}

        """

        Drawable.set_path(self, path)
        for sprite in self.innerSprites():
            sprite.path.follow(path)
            sprite.move()

    def runPath(self, frames=0):
        """Move along the path. This is used only in an interactive
        session.

        @param frames: Number of moves to make before raising
        L{Path.EndOfPath}.

        """

        count = 0
        #screen = self.screen
        #bg = self.bg
        while count < frames or not frames:
            self.clear()
            try:
                self.move()
                for sprite in self.innerSprites():
                    sprite.move()
            except Path.EndOfPath:
                self.path.reset()
                raise
            areas = self.draw()
            pygame.display.update(areas)
            count += 1

    def move(self):
        """Move sprite to next location along path."""

        try:
            self.set_position(self.path.next())
            for sprite in self.innerSprites():
                sprite.move()
        except StopIteration:
            raise Path.EndOfPath

    def collide(self, other):
        """return True if this sprite and other sprite overlap.

        Uses the C{.crect} attribute of each sprite to check for
        a collision (overlap).

        @param other: The other sprite to check for collision.

        @returns: True if the sprites overlap.
        @rtype: C{bool}

        """

        for sprite in self.innerSprites():
            if sprite.crect.colliderect(other.crect):
                return True
        return False

    def collidelist(self, lothers):
        """return True if this sprite and any in list of others collide.

        The True value is the other sprite. Note that more than one sprite in
        the list may be colliding with the sprite, but only one is returned.

        @param lothers: List of other sprites to check for collision.

        @returns: Other sprite if there is a collision, or C{False}.
        @rtype: C{Drawable} or C{False}

        """

        rects = [o.crect for o in lothers]

        for sprite in self.innerSprites():
            index = sprite.crect.collidelist(rects)
            if index != -1:
                return lothers[index]
        return 0

    def collidelistall(self, lothers):
        """return True if this sprite and any in list of others collide.

        The True value is the list of colliding sprites, or if there is no
        collision, an empty sequence.

        @param lothers: List of other sprites to check for collision.

        @returns: List of colliding sprites, or empty list.
        @rtype: C{List}

        """

        rects = [o.crect for o in lothers]

        indexes = self.crect.collidelistall(rects)
        if not indexes:
            return []
        else:
            return [lothers[index] for index in indexes]

class Stationary(Drawable):
    """Drawable things which never move.

    These will be drawn directly on to the background, and
    the background underneath will be saved for easy
    restoration later.

    Using a C{Stationary} sprite instead will save resources since
    they do not need to be redrawn each frame.

    """

    def __init__(self, w=None, sprite=None):
        """Initialize the sprite.

        @param w: C{Layer} on which the sprite will be drawn.
        @param sprite: C{Drawable} from which to get the image.
            Uses the C{.image} attribute of the sprite.

        """

        if sprite is None:
            sprite = Image()
        self.sprite = sprite
        Drawable.__init__(self, w)
        self.prepare()
        self.crect = pygame.Rect(self.rect)

    def prepare(self):
        """Save a copy of the background underneath where the sprite
        will be drawn.

        """

        sprite = self.sprite
        self.image = sprite.image
        self.rect = sprite.rect
        self.bg = pygame.Surface(self.image.get_size())

        self.bg.blit(self.window.bg, (0, 0), self.rect)

    def draw(self):
        """Blit image to both background and foreground."""

        rect = self.rect
        self.window.bg.blit(self.image, rect)
        self.window.screen.blit(self.image, rect)
        pygame.display.update(rect)

    def clear(self):
        """Blit saved background to both background and foreground."""

        #print 'both', id(self.window.bg), id(self.bg)
        w, h = self.rect.size
        r = pygame.Rect(0, 0, w, h)
        #self.bg.fill((0,0,255))
        self.window.bg.blit(self.bg, self.rect, r)
        self.window.screen.blit(self.bg, self.rect, r)
        #print 'updating stationary'
        #print 'statrect', self.rect
        pygame.display.update(self.rect)

    def set_position(self, position):
        """Move the sprite.

        Clears out old position and re-draws at new position.

        """

        self.clear()
        self.sprite.set_position(position)
        self.prepare()
        self.draw()

    def get_position(self):
        """Return current position"""

        return self.sprite.get_position()

    def move(self):
        """Does nothing.

        Useful if you want to be able to call move() on a whole group
        of sprites without checking to see if they want to move or not.

        """

        pass


class StationaryStack:
    """A Stack of Stationary Drawables.

    This is useful to keep the Stationary objects in order
    so that the background can be properly restored as
    they are cleared.

    """

    def __init__(self, w=None):
        if w is None:
            if hasattr(conf, 'window'):
                w = conf.window
                #print 'aaa', w
            else:
                w = Screen.Window()
                #print 'bbb', w
        self.window = w
        self.stack = []

    def push(self, stationary):
        """Add another sprite on top of the stack."""

        if not issubclass(stationary.__class__, Stationary):
            #print 'making stationary'
            stationary = Stationary(self.window, stationary)
        stationary.draw()
        #print 'adding', id(stationary), stationary.get_position()
        self.stack.append(stationary)

    def pop(self):
        """Remove the top sprite from the stack."""

        try:
            stationary = self.stack.pop()
            #print 'clearing', id(stationary), stationary.get_position()
        except IndexError:
            #print 'done'
            return 0
        stationary.clear()
        return 1

    def empty(self):
        """Remove all of the sprites from the stack."""

        while 1:
            if not self.pop():
                pygame.display.update()
                break


class Turtle(RotatedImage):
    """Turtle-graphics-like object"""

    COLOR = WHITE
    BGCOLOR = BLACK

    def __init__(self, w=None, position=None, deg=90, color=None,
                    filename='turtle.png', colorkey=TRANSPARENT, convert=1):
        RotatedImage.__init__(self, w=w, filename=filename, steps=60, colorkey=colorkey,
                                convert=convert)
        self._window = self.window
        self.saved_state = []

        self._filling = 0
        self._to_fill = []

        if position is None:
            self.center()
            position = self.get_position()
        else:
            self.set_position(position)
        self.position_original = self.get_position()[:]

        self.deg_original = deg % 360

        self.set_visible()
        if color is None:
            color = self.COLOR
        self.set_color(color)
        self.bgColor = BLACK
        self.set_background()
        self.set_background(self.BGCOLOR)
        self.set_fontSize()
        self.set_width(2)
        self.penDown()
        self.uclear()

        path = Path.TurtlePath(position, deg)
        self.set_path(path)

        self.turnTo(90)
        self.set_closest()
        self.move()
        self.udraw()

        self.set_crect(self.rect)


    def begin(self, interactive=1):
        """Start a new layer for drawing.

        Use commit() to copy layer to the base window, or
        use rollback() to throw away the layer and
        return to drawing directly to the base window.

        """

        if self.saved_state:
            # only supports one-level of transaction right now
            # should not be too tough to extend this to more
            raise NotImplementedError

        self.transaction_interactive = interactive

        self.uclear()
        self._window.clear()
        self.saved_state.append((self.get_position(), self.get_deg(), self.window))
        self.window = Layer(color=self.bgColor)
        self.screen = self.window.screen
        self.bg = self.window.bg
        self.screen.set_colorkey(self.bgColor)
        self.bg.set_colorkey(self.bgColor)
        if self.visible and interactive:
            self.draw()
        self.update()

    def begin_fill(self):
        """Start saving points for filling a polygon later

        Each move pushes the current point in to a list.
        Use commit_fill() to fill inside of the points
        use rollback_fill() to throw away the list without
        filling.

        """

        if self._filling:
            # not sure what it would mean, to try filling
            # again whil already filling... safest to error out
            return NotImplementedError

        self._to_fill = [self.get_position()]
        self._filling = 1

    def commit(self):
        """Copy drawing layer to base window.

        """

        if not self.saved_state:
            # not in transaction
            return

        self.uclear()
        self.window.draw()
        position, deg, window = self.saved_state.pop()
        window.bg.blit(self.bg, (0, 0))
        self.window = window
        self.screen = self.window.screen
        self.bg = self.window.bg
        self.window.clear()
        if self.visible:
            self.draw()
        self.update()

    def commit_fill(self, color=None):
        """Fill the polygon of saved points

        Start saving points for fill with begin_fill()

        Fill is done with pygame.draw.polygon, so if the
        line of points crosses itself, the fill will turn
        inside out.

        """

        if not self._filling:
            # was not filling
            return

        c = self.color
        if color is not None:
            self.set_color(color)

        pygame.draw.polygon(self.window.screen, self.color,
                                            self._to_fill, 0)
        dirty = [pygame.draw.polygon(self.window.bg, self.color,
                                            self._to_fill, 0)]

        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)

        self._filling = 0
        self._to_fill = []

        self.set_color(c)

    def rollback(self):
        """Throw out drawing layer.

        """

        if not self.saved_state:
            # not in transaction
            return

        self.clear()
        position, deg, window = self.saved_state.pop()
        self.moveTo(position)
        self.turnTo(deg)
        self.window = window
        self.screen = self.window.screen
        self.bg = self.window.bg
        self._window.clear()
        if self.visible:
            self.draw()
        self.update()

    def rollback_fill(self):
        """Throw out list of saved points

        """

        self._filling = 0
        self._to_fill = []

    def draw(self, surface=None):
        """draw image, returning affected rect"""

        if self.saved_state and self.transaction_interactive:
            self._window.screen.blit(self.image, self.rect)
        Drawable.draw(self, surface)

        return pygame.Rect(self.rect)

    def clear(self, surface=None):
        """erase sprite image to background, returning affected rect"""

        Drawable.clear(self, surface)
        if self.saved_state and self.transaction_interactive:
            self._window.clear()
            self.update()

        return pygame.Rect(self.rect)

    def update(self, dirty=None):
        """Update the display"""

        if self.saved_state:
            #print 'updating'
            if self.transaction_interactive:
                self._window.screen.blit(self.bg, (0, 0))
                self._window.update()
        else:
            #print 'normal'
            self._window.update(dirty)


    def set_background(self, color=None):
        """Set the background color

        Saves the current picture before changing the background color
        and restores the picture afterward. The picture may not be quite
        the same if parts of it were drawn using the old bg color.

        """

        if color is None:
            color = self.bgColor

        save = pygame.Surface(self.window.screen.get_size())
        save.blit(self.bg, (0, 0))
        save.set_colorkey(self.bgColor)

        self.bgColor = color
        self.window.set_background(color=color)

        self.screen.blit(save, (0, 0))
        self.bg.blit(save, (0, 0))
        if self.visible:
            self.draw()
        self.update()

    def set_width(self, width):
        """Set line width for drawing.

        @param width: line width in pixels

        """

        self.width = width

    def clearScreen(self):
        """Clear the screen to background color.

        Does not move the Penguin.

        I am considering a shorter name, perhaps cls

        """

        self.window.set_background(color=self.bgColor)
        self.bg = self.window.bg
        self.window.clear()
        if self.visible:
            self.draw()
        self.update()

    def reset(self):
        """Clear the screen to LBLUE, and return Penguin to home

        also reset pen color to WHITE, and turn back to 90 deg
        (standing straight up)

        """

        self.rollback_fill()
        self.rollback()

        self.uclear()
        self.set_color(self.COLOR)
        self.bgColor = self.BGCOLOR
        self.rollback_fill()
        self.show()
        self.penDown()
        self.moveTo(self.position_original)
        self.move()
        self.turnTo(90)
        self.set_closest()
        self.clearScreen()

    def refresh(self):
        """Update the display.

        This is useful when your system does not automatically refresh
        the screen after it gets covered up and then uncovered.

        """

        self.update()

    def shrink(self, dx=50, dy=50):
        """Resize the window (smaller)

        @param dx: horizontal amount to reduce size
        @param dy: vertical amount to reduce size

        """

        w, h = pygame.display.get_surface().get_size()
        w -= dx
        h -= dy
        conf.WINWIDTH = w
        conf.WINHEIGHT = h
        conf.WINSIZE = (conf.WINWIDTH, conf.WINHEIGHT)
        self.window.resize(conf.WINSIZE)
        homeX = conf.WINWIDTH / 2
        homeY = conf.WINHEIGHT / 2
        self.set_home((homeX, homeY))
        self.reset()

    def grow(self, dx=50, dy=50):
        """Resize the window (larger)

        @param dx: horizontal amount to increase size
        @param dy: vertical amount to increase size

        """

        self.shrink(-dx, -dy)

    def save(self, filename):
        """Save background (the picture) as filename

        @param filename: name of file to save the image to.
        if filename ends with .bmp it will be saved
        as a bmp (bitmap), otherwise, the filename
        will be made to end with .tga (if it does not
        already) and the file will be saved as a tga file.
        """

        if not filename.endswith('.tga') and not filename.endswith('.bmp'):
            filename += '.tga'
        pygame.image.save(self.bg, filename)

    def set_home(self, pos=None):
        """Set the Penguin's home position"""

        if pos is None:
            self.set_home(self.get_position())
        else:
            self.position_original = pos

    def home(self):
        """Move back to the home position"""

        self.turnTo(90)
        self.moveTo(self.position_original)

    def penDown(self):
        """Put pen down, ready to draw"""

        self.pen = 1

    def penUp(self):
        """Pull pen up. Most movement will not make a mark.

        Note that some functions (circle notably) do not pay
        any attention to the state of the pen.

        """
        self.pen = 0

    def set_visible(self, vis=1):
        """Set the penguin icon visible"""

        self.visible = vis
        if not vis:
            self.uclear()
        else:
            self.udraw()

    def show(self):
        """Set the penguin icon visible"""

        self.set_visible(1)

    def hide(self):
        """Set the penguin icon invisible"""

        self.set_visible(0)

    def set_color(self, color=None, r=None, g=None, b=None):
        """Set the color for drawing.

        The caller can choose one of a few ways to set the color:
            - an RGB tuple can be passed in as the C{color} parameter
                (or as the first argument)
            - one or more of C{r}, C{g}, and C{b} parameters can (also) be
                passed as that portion of the color tuple.

                If these are given in addition to the C{color} parameter,
                these will override the elements in the C{color} tuple.
                I{ie. C{set_color((10, 10, 10), r=50)} will set the color
                to C{(50, 10, 10)}}

                If these are given with NO color tuple passed, the resulting
                color will start with the current color, with the new elements
                being set from the passed parameters I{ie, if the color is
                C{(100, 100, 100)} before the call, calling
                C{set_color(g=50, b=50)} will set the color to C{(100, 50, 50)}}

            - if no parameters are passed at all, the color is set to WHITE.

        @param color: an RGB tuple, or the word 'random' which will choose
            a color at random from (not quite) all possible.
        @param r: The red value of the color (0 - 255)
        @param g: The green value of the color (0 - 255)
        @param b: The blue value of the color (0 - 255)

        """

        if color is None and r is None and g is None and b is None:
            # Use the ColorSelector Widget
            import Widget
            color = Widget.Dialog_ColorSelector().modal()
            if color is not None:
                r, g, b = color
            else:
                r, g, b = WHITE

        elif color is None:
            rr, rg, rb = self.color
        elif color == 'random':
            rr = random.randint(50, 250)
            rg = random.randint(50, 250)
            rb = random.randint(50, 250)
        elif color:
            rr, rg, rb = color

        if r is not None:
            rr = r
        if g is not None:
            rg = g
        if b is not None:
            rb = b

        color = (rr, rg, rb)
        self.color = color

    def nudge_color(self, red=None, blue=None, green=None):
        """Change the pen color by given amounts.

        Amounts can be either integer numbers (to be added to the RGB
        tuple components), or percentages (to increase or decrease
        that component by given percent)

        I{ie, if color is C{(100, 100, 100)} before the call, a call to
        C{nudge_color(red=50, blue=-10, green="75%")} will result in the
        color being set to C{(150, 90, 75)}}

        @param red: Amount to add to R element of color tuple OR a
            string with the amount to increease the R element.
        @param green: Amount to add to G element of color tuple OR a
            string with the amount to increease the G element.
        @param blue: Amount to add to B element of color tuple OR a
            string with the amount to increease the B element.

        """

        r, g, b = self.color
        if red is not None:
            try:
                r += red
            except TypeError:
                r *= (float(red[:-1]) / 100.0)
        if blue is not None:
            try:
                b += blue
            except TypeError:
                b *= (float(blue[:-1]) / 100.0)
        if green is not None:
            try:
                g += green
            except TypeError:
                g *= (float(green[:-1]) / 100.0)

        r = min(r, 255)
        g = min(g, 255)
        b = min(b, 255)
        r = max(r, 0)
        g = max(g, 0)
        b = max(b, 0)

        self.set_color((r, g, b))

    def forward(self, dist):
        """Move the turtle forward a distance

        @param dist: Number of pixels to move.

        """

        dirty = [self.clear()]
        positionOld = self.get_position()
        self.path.forward(dist)
        self.move()
        position = self.get_position()
        if self.pen:
            dirty.append(self.line(position, positionOld))
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)

        if self._filling:
            self._to_fill.append(position)

    def backward(self, dist):
        """Move the turtle backward distance.

        eqivalent to forward(-dist)

        @param dist: Number of pixels to move.

        """

        self.forward(-dist)

    def moveTo(self, position):
        """Move turtle to position, without drawing a line

        @param position: Point C{(x, y)} to move to

        """

        dirty = [self.clear()]
        if position == 'random':
            x = random.randint(0, conf.WINWIDTH)
            y = random.randint(0, conf.WINHEIGHT)
            position = (x, y)
        self.set_position(position)
        self.move()
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)

        if self._filling:
            self._to_fill.append(position)

    def lineTo(self, position):
        """Move turtle to position, drawing a line

        Note that this ignores the state of the pen (up or down) and
        always draws a line in the current pen color.

        @param position: Point C{(x, y)} to draw the line to.

        """

        pen = self.pen
        self.penDown()
        positionOld = self.get_position()
        if self.visible:
            dirty = [self.clear()]
        else:
            dirty = []
        self.path.set_position(position)
        dirty.append(self.line(position, positionOld))
        self.moveTo(position)
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)

    def line(self, p1, p2):
        """Draw a line segment between 2 points.

        This function ignores the state of the pen. In other words, it
        will draw a line to the screen in the current color even if the
        turtle's pen is up.

        @param p1: One endpoint of line segment.
        @param p2: Second endpoint of line segment.

        """

        dirty = pygame.draw.line(self.bg, self.color, p1, p2, self.width)
        self.screen.blit(self.bg, dirty, dirty)

        return dirty

    def left(self, d):
        """Turn left (counter-clockwise) a number of degrees

        @param d: Number of degrees to rotate counter-clockwise.

        """

        deg = self.path.get_deg()
        deg += d
        self.turnTo(deg)

    def right(self, d):
        """Turn right (clockwise) a number of degrees

        @param d: Number of degrees to rotate clockwise.

        """

        self.left(-d)

    def turnTo(self, deg):
        """Set turtle's direction to deg (degrees).


        @param deg: Direction to turn to. 0 degrees is along the positive x-axis.

        """

        dirty = [self.clear()]
        if deg == 'random':
            deg = random.randint(0, 360)
        self.path.set_deg(deg)
        self.set_rotation((deg/180.0) * PI)
        self.move()
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)

    def get_deg(self):
        """return current turtle direction.

        Zero (0) degrees is along the positive x-axis.

        """

        return self.path.get_deg()

    def circle(self, radius, clockwise=1, color=None, width=None):
        """Quick drawing circle. Starting from current position and rotation.

        "Quick drawing" means that this function draws the circle by calling
        L{pygame.draw.circle} and not by simulating the drawing of a circle
        with a number of line segments and turns, which would be much slower.

        @param radius: Radius of circle to draw. The center will be 90 degrees
            from the current direction.
        @param clockwise: Draw the circle turning clockwise from the current
            position, or if False, turn counter-clockwise.
        @param color: Color to use for drawing circle, or the string 'random'
            to choose a random color. Does not affect the turtle's pen color
            (ie, the pen color will be restored before returning)
        @param width: Thickness of line to use when drawing, or Zero (0) to
            fill with color.

        """

        save_color = self.color
        if color is None:
            color = self.color
        elif color == 'random':
            self.set_color('random')
            color = self.color

        if radius < 0:
            radius = -radius
            clockwise = not clockwise
        elif radius == 0:
            return

        x, y = self.get_position()
        rad = self.path.get_direction()
        if clockwise:
            toCenter = rad - PI/2
        else:
            toCenter = rad + PI/2

        cx = int(x + (radius * math.cos(toCenter)))
        cy = int(y - (radius * math.sin(toCenter)))
        radius = int(radius)

        if width is None:
            # width must be less than radius
            width = min(self.width, radius)

        rect = pygame.draw.circle(self.bg, color, (cx, cy), radius, width)
        dirty = [self.screen.blit(self.bg, rect, rect)]
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)
        self.set_color(save_color)

    def cCircle(self, radius, color=None, width=None):
        """Quick drawing circle, centered on current position.

        Does not move the turtle (ie, the turtle will be returned to its
        present location before returning)

        "Quick drawing" means that this function draws the circle by calling
        L{pygame.draw.circle} and not by simulating the drawing of a circle
        with a number of line segments and turns, which would be much slower.

        @param radius: Radius of circle to draw. The center will be the
            current location.
        @param color: Color to use for drawing circle, or the string 'random'
            to choose a random color. Does not affect the turtle's pen color
            (ie, the pen color will be restored before returning)
        @param width: Thickness of line to use when drawing, or Zero (0) to fill
            with color.

        """


        save_color = self.color
        if color is None:
            color = self.color
        elif color == 'random':
            self.set_color('random')
            color = self.color

        if width is None:
            # width must be less than radius
            width = min(self.width, radius)

        if radius < 0:
            radius = -radius
        elif radius == 0:
            return

        cx, cy = self.get_position()
        cx = int(cx)
        cy = int(cy)
        radius = int(radius)
        rect = pygame.draw.circle(self.bg, color, (cx, cy), radius, width)
        dirty = [self.screen.blit(self.bg, rect, rect)]
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)
        self.set_color(save_color)

    def set_fontSize(self, fontSize=40):
        """Set default font size for L{write} and L{where}"""

        self.fontSize = fontSize

    def write(self, text, fontSize=None, color=None, bgColor=TRANSPARENT):
        """Draw text from current position, and at current angle.

        @param fontSize: text font size.
        @param color: RGB tuple. color of text
        @param bgColor: background color

        """

        saveFontSize = self.fontSize
        if fontSize is not None:
            self.set_fontSize(fontSize)
        size = self.fontSize
        if color is None:
            color = self.color
        font = pygame.font.Font(None, size)
        image = font.render(text, 1, color, bgColor)
        tw, th = image.get_size()
        if bgColor == TRANSPARENT:
            image.set_colorkey(TRANSPARENT)
        deg = self.path.get_deg()
        rad = self.path.get_direction()
        image = pygame.transform.rotate(image, deg)
        w, h = image.get_size()
        x, y = self.get_position()
        if 0 <= deg < 90:
            ix = x - (th * math.sin(rad))
            iy = y - h
        elif 90 <= deg < 180:
            ix = x - w
            iy = y - (tw * math.sin(rad))
        elif 180 <= deg < 270:
            ix = x + (tw * math.cos(rad))
            iy = y
        else:
            ix = x
            iy = y - (th * math.cos(rad))
        self.bg.blit(image, (ix, iy))
        dirty = [self.screen.blit(image, (ix, iy))]
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)
        self.set_fontSize(saveFontSize)
        return tw

    def where(self):
        """Briefly show the current position of the turtle."""

        pos = self.get_position()
        m = "(%.1f, %.1f)" % (pos[0], pos[1])
        s = String(message=m, fontSize=self.fontSize, color=self.color)
        s.set_position(pos)
        stat = Stationary(sprite=s)
        stat.draw()
        pygame.time.wait(400)
        stat.clear()
        if self.visible:
            self.udraw()

    def rectangle(self, side_length=20, side_width=10, clockwise=1, width=None,
                    color=None, bgColor=TRANSPARENT):
        """Quick drawing routine for rectangles.

        @param side_length: length of 1st and 3rd sides drawn
        @param side_width: length of 2nd and last sides drawn
        @param clockwise: all turns will be 90 degrees right
            clockwise 0 means all turns will be 90 degrees left
        @param width: thickness of outline of rectangle
            width 0 means rectangle should be filled with color
        @param color: RGB tuple, color of rectangle
        @param bgColor: background color. Note that rectangle is not constrained
            to align horizontally or verically.

        """

        if not side_length > 0 or not side_width > 0:
            raise ZeroDivisionError

        deg_original = self.path.get_deg()

        if clockwise:
            self.path.set_deg(deg_original-90)
            side_length, side_width = side_width, side_length

        if color is not None:
            self.set_color(color)

        if width is None:
            width = self.width

        side_length = int(side_length)
        side_width = int(side_width)
        image = pygame.Surface((side_length, side_width))
        rect = image.get_rect()
        if bgColor:
            image.fill(bgColor)
        pygame.draw.rect(image, self.color, rect, width)
        tw, th = image.get_size()
        image.set_colorkey(TRANSPARENT)
        deg = self.path.get_deg()
        rad = self.path.get_direction()
        image = pygame.transform.rotate(image, deg)
        w, h = image.get_size()
        x, y = self.get_position()
        if 0 <= deg < 90:
            ix = x - (th * math.sin(rad))
            iy = y - h
        elif 90 <= deg < 180:
            ix = x - w
            iy = y - (tw * math.sin(rad))
        elif 180 <= deg < 270:
            ix = x + (tw * math.cos(rad))
            iy = y
        else:
            ix = x
            iy = y - (th * math.cos(rad))
        self.bg.blit(image, (ix, iy))
        dirty = [self.screen.blit(image, (ix, iy))]
        self.path.set_deg(deg_original)
        if self.visible:
            dirty.append(self.draw())
        self.update(dirty)


    def cRectangle(self, side_length=20, side_width=10, width=None,
                    color=None, bgColor=TRANSPARENT):
        """Quick drawing routine for rectangles.

        Rectangle is centered on current position.

        @param side_length: length of 1st and 3rd sides drawn
        @param side_width: length of 2nd and last sides drawn
        @param width: thickness of outline of rectangle
            width 0 means rectangle should be filled with color
        @param color: RGB tuple, color of rectangle
        @param bgColor: background color. Note that rectangle is not constrained
            to align horizontally or verically.

        """

        pen = self.pen

        self.penUp()
        self.forward(side_length / 2)
        self.right(90)
        self.forward(side_width / 2)
        self.right(90)

        if pen:
            self.penDown()
        self.rectangle(side_length, side_width, width=width,
                        color=color, bgColor=bgColor)

        self.penUp()
        self.forward(side_length / 2)
        self.right(90)
        self.forward(side_width / 2)
        self.right(90)

        if pen:
            self.penDown()

    def square(self, side_length=20, clockwise=1, width=None,
                    color=None, bgColor=TRANSPARENT):
        """Quick drawing square.

        @param side_length: length of all sides drawn
        @param clockwise: all turns will be 90 degrees right
            clockwise 0 means all turns will be 90 degrees left
        @param width: thickness of outline of square
            width 0 means square should be filled with color
        @param color: RGB tuple, color of square
        @param bgColor: background color. Note that square is not constrained
            to align horizontally or verically.

        """

        self.rectangle(side_length, side_length, clockwise=clockwise,
                        width=width, color=color, bgColor=bgColor)

    def cSquare(self, side_length=20, width=None,
                    color=None, bgColor=TRANSPARENT):
        """Quick drawing routine for squares.

        Square is centered on current position.

        @param side_length: length of all sides drawn
        @param width: thickness of outline of square
            width 0 means square should be filled with color
        @param color: RGB tuple, color of square
        @param bgColor: background color. Note that square is not constrained
            to align horizontally or verically.

        """

        pen = self.pen

        self.penUp()
        self.forward(side_length / 2)
        self.right(90)
        self.forward(side_length / 2)
        self.right(90)

        if pen:
            self.penDown()
        self.square(side_length, width=width, color=color, bgColor=bgColor)

        self.penUp()
        self.forward(side_length / 2)
        self.right(90)
        self.forward(side_length / 2)
        self.right(90)

        if pen:
            self.penDown()

    def wait(self):
        """Read pygame events until mouse click or any key press."""

        done = 0
        events = pygame.event.get()
        while not done:
            for e in events:
                if (e.type == MOUSEBUTTONDOWN or
                        e.type == KEYDOWN or
                        e.type == QUIT):
                    done = 1
                    break
            events = pygame.event.get()

    def blink(self, times=1, delay=350):
        """Flash the turtle on and off.

        @param times: Number of times to flash.
        @param delay: Length of flash, and delay between flashes (in millisecond).

        """
        vis = self.visible
        while times:
            self.set_visible(1)
            pygame.time.wait(delay)
            self.set_visible(0)
            pygame.time.wait(delay)
            times -= 1
        self.set_visible(vis)


class EuclidTurtle(Turtle):
    """Turtle with altered co-ordinate system.

    Instead of (0, 0) being the upper left corner of the
    screen, the origin is the center of the screen. The
    EuclidTurtle also uses a different scale: each unit is
    by default 30 pixels.

    """

    def __init__(self, w=None, position=None, deg=0, color=WHITE,
                    filename='turtle.png', colorkey=TRANSPARENT, convert=1):
        Turtle.__init__(self, w, position, deg, color, filename, colorkey, convert)
        self.euclidean()

    def reset(self):
        Turtle.reset(self)
        self.euclidean()

    def euclidean(self, drawCoords=1):
        """Set up the coordinate system. """

        self.euclid_cx = conf.WINWIDTH / 2
        self.euclid_cy = conf.WINHEIGHT / 2
        self.euclid_mult = 30.0
        self.maxX = self.euclid_cx / self.euclid_mult
        self.maxY = self.euclid_cy / self.euclid_mult
        if drawCoords:
            self.drawEuclidCoords()
        self.set_home((0, 0))
        self.home()

    def drawEuclidCoords(self):
        """Draw the cartesian (x, y) coordinate system."""

        color = self.color
        self.set_color(LRED)
        maxX = int(self.euclid_cx / self.euclid_mult)
        maxY = int(self.euclid_cy / self.euclid_mult)
        self.moveTo((-maxX, 0))
        self.lineTo((maxX, 0))
        self.moveTo((0, -maxY))
        self.lineTo((0, maxY))
        self.turnTo(0)
        for y in range(-maxY, maxY):
            self.moveTo((0, y))
            self.lineTo((0.25, y))
            self.write("%3s" % (y), fontSize=12)
        for x in range(-maxX, maxX):
            self.moveTo((x, 0))
            self.lineTo((x, -0.25))
            self.moveTo((x, -0.4))
            self.write("%3s" % (x), fontSize=12)
        self.set_color(color)

    def euclid_translate(self, position):
        """Convert to real screen coordinates."""

        x, y = position
        mult = self.euclid_mult
        euclid_x = (x - self.euclid_cx) / mult
        euclid_y = (self.euclid_cy - y) / mult
        return (euclid_x, euclid_y)

    def euclid_untranslate(self, position):
        """Convert from real screen coordinates."""

        euclid_x, euclid_y = position
        mult = self.euclid_mult
        x = (euclid_x * mult) + self.euclid_cx
        y = self.euclid_cy - (euclid_y * mult)
        return (x, y)

    def euclid_scale(self, dist):
        """Scale a distance to a real screen distance."""

        return dist / self.euclid_mult

    def euclid_unscale(self, dist):
        """Scale a distance from a real screen distance."""

        return dist * self.euclid_mult

    def moveTo(self, position):
        dirty = [self.clear()]
        if position == 'random':
            x = random.randint(0, conf.WINWIDTH)
            y = random.randint(0, conf.WINHEIGHT)
            position = (x, y)
        p = self.euclid_untranslate(position)
        self.path.set_position(p)
        self.move()
        if self.visible:
            dirty.append(self.draw())
        self.window.update(dirty)

    def lineTo(self, position):
        pen = self.pen
        self.penDown()
        positionOld = self.get_position()
        positionOld = self.euclid_translate(positionOld)
        if self.visible:
            dirty = [self.clear()]
        else:
            dirty = []
        p = self.euclid_untranslate(position)
        self.path.set_position(p)
        dirty.append(self.lineSegment(position, positionOld))
        self.moveTo(position)
        if self.visible:
            dirty.append(self.draw())
        self.window.update(dirty)

    def lineSegment(self, p1, p2):
        """Draw a line segment between 2 points.

        This function ignores the state of the pen.

        @param p1: One endpoint of line segment.
        @param p2: Second endpoint of line segment.

        """

        p1 = self.euclid_untranslate(p1)
        p2 = self.euclid_untranslate(p2)
        x, y = p1
        xO, yO = p2
        dirty = pygame.draw.line(self.bg, self.color,
                                (x, y), (xO, yO), self.width)
        self.screen.blit(self.bg, dirty, dirty)
        return dirty

    def line(self, p1, p2):
        """Draw a line which includes these 2 points.

        Unlike C{Turtle.line} this will draw as much of the line as will fit
        on the screen, not just a line segment connecting the two points.

        This function ignores the state of the pen.

        @param p1: One point on the line.
        @param p2: Second point on the line.

        """

        x, y = p1
        x0, y0 = p2
        if x - x0:
            m = (float(y - y0)) / (x - x0)
        else:
            m = 999999

        self.line_point_slope(p1, m)

    def line_point_slope(self, p, m):
        """Draw a line through a point with a slope.

        This function ignores the state of the pen.

        @param p: One point on the line.
        @param m: Slope of the line.

        """

        x0, y0 = p
        if m:
            y1 = self.maxY
            x1 = ((y1 - y0) / m) + x0
            y2 = -y1
            x2 = ((y2 - y0) / m) + x0
        else:
            y1 = 0
            x1 = self.maxX + 1
            y2 = 0
            x2 = -self.maxX - 1
        x3 = self.maxX
        y3 = (m * (x3 - x0)) + y0
        x4 = -x3
        y4 = (m * (x4 - x0)) + y0

        if x1 > self.maxX:
            xa = x3
            ya = y3
        else:
            xa = x1
            ya = y1
        if x2 < - self.maxX:
            xb = x4
            yb = y4
        else:
            xb = x2
            yb = y2

        xa, ya = self.euclid_untranslate((xa, ya))
        xb, yb = self.euclid_untranslate((xb, yb))

        dirty = pygame.draw.line(self.window.bg, self.color,
                                (xa, ya), (xb, yb), self.width)
        self.screen.blit(self.bg, dirty, dirty)
        return dirty

    def forward(self, dist):
        dirty = [self.clear()]
        positionOld = self.get_position()
        pOld = self.euclid_translate(positionOld)
        d = self.euclid_unscale(dist)
        self.path.forward(d)
        self.move()
        position = self.get_position()
        p = self.euclid_translate(position)
        if self.pen:
            dirty.append(self.lineSegment(p, pOld))
        if self.visible:
            dirty.append(self.draw())
        self.window.update(dirty)

    def cSquare(self, side_length=2, width=None,
                    color=None, bgColor=TRANSPARENT):
        l = self.euclid_unscale(side_length)

        pen = self.pen

        self.penUp()
        self.forward(side_length / 2.0)
        self.right(90)
        self.forward(side_length / 2.0)
        self.right(90)

        if pen:
            self.penDown()
        Turtle.rectangle(self, l, l, clockwise=1, width=width,
                            color=color, bgColor=bgColor)

        self.penUp()
        self.forward(side_length / 2.0)
        self.right(90)
        self.forward(side_length / 2.0)
        self.right(90)

        if pen:
            self.penDown()


    def square(self, side_length=20, clockwise=1, width=None,
                    color=None, bgColor=TRANSPARENT):
        l = self.euclid_unscale(side_length)
        Turtle.rectangle(self, l, l, clockwise=clockwise,
                        width=width, color=color, bgColor=bgColor)



    def cRectangle(self, side_length=20, side_width=10, width=None,
                    color=None, bgColor=TRANSPARENT):
        l = self.euclid_unscale(side_length)
        w = self.euclid_unscale(side_width)
        Turtle.cRectangle(self, l, w, width, color, bgColor)

    def rectangle(self, side_length=20, side_width=10, clockwise=1, width=None,
                    color=None, bgColor=TRANSPARENT):
        l = self.euclid_unscale(side_length)
        w = self.euclid_unscale(side_width)
        Turtle.rectangle(self, l, w, clockwise, width, color, bgColor)

    def where(self):
        pos = self.get_position()
        p = self.euclid_translate(pos)
        s = String(self.w, "(%.1f, %.1f)" % p,
                    fontSize=self.fontSize, color=self.color)
        s.set_position(pos)
        stat = Stationary(self.window, s)
        stat.draw()
        pygame.time.wait(400)
        stat.clear()
        if self.visible:
            self.udraw()

    def circle(self, radius, clockwise=1, color=None, width=None):
        r = self.euclid_unscale(radius)
        Turtle.circle(self, r, clockwise, color, width)

    def cCircle(self, radius, color=None, width=None):
        r = self.euclid_unscale(radius)
        Turtle.cCircle(self, r, color, width)
