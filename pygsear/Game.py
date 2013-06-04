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

"""Game is the central object. It should create all of the
objects in the game, then control them in the mainloop()

"""

import time, random, math, os

import pygame
import pygame.draw
from pygame.locals import K_RETURN, K_ESCAPE, K_f, K_s, K_PAGEUP, K_PAGEDOWN

import conf
import Screen
import Drawable
from Drawable import SpriteGroup
import Widget
import Path
import Cursor
import Event
from locals import BLACK, RED, LBLUE, LGREEN

class GameLooper:
    """Abstract game control class"""

    def __init__(self):
        self.events = Event.EventGroup()
        self.events.add(Event.QUIT_Event(callback=self._quit))

        self.sprites = self.addGroup()

        self.layers = []

        self.quit = 0
        self.stop = 0

    def pause(self):
        for sprite in self.sprites.sprites():
            sprite.pause()

    def unpause(self):
        for sprite in self.sprites.sprites():
            sprite.unpause()

    def beep(self):
        print chr(7)

    def loop(self):
        while not self.quit and not self.stop:
            self.sprites.clear()
            self.checkEvents()
            dirty = self.sprites.draw()
            pygame.display.update(dirty)

        self.stop = 0
        pygame.event.get()

    def checkEvents(self):
        self.events.check()

    def checkCollisions(self):
        """Defaults to no collision checks.
        
        Game.mainloop() will call this function once each time through
        the loop. Subclasses should override to check collisions and
        perform the needed actions.
        
        """
        
        pass

    def addGroup(self, sprites=[], layer=None):
        """return a L{SpriteGroup}

        At this point, this is just a convenience to get a new Group,
        but it could at some point in the future keep track of all
        groups in the Game.

        """

        if layer is None:
            layer = self.window
        return SpriteGroup(layer, sprites)

    def addEventGroup(self, event=()):
        """return a L{Event.EventGroup}

        At this point, this is just a convenience to get a new Group,
        but it could at some point in the future keep track of all
        groups in the Game.

        """

        return Event.EventGroup(event)

    def addLayer(self, size=None):
        """return a L{Drawable.Layer} and keep track.

        Each C{Game} has a list (C{.layers}) of all the layers
        in the game.

        """

        layer = Drawable.Layer(size=size)
        self.layers.append(layer)
        return layer

    def _stop(self, arg=None):
        """set the C{.stop} attribute.

        This should cause a break on the next loop.

        """

        self.stop = 1

    def _quit(self, arg=None):
        """set the C{.quit} attribute.

        This should cause a break on the next loop, and should
        also cause the Game to end and the program to exit.

        """

        self.quit = 1


class GameConfiguration(Drawable.Layer, GameLooper):
    """Used to configure the game
    
    Right now, this allows choice of video mode, fullscreen/window,
    and allows the configuration to be saved on unix systems.
    
    Eventually, it should be possible to configure keybindings
    here also, and to create generalized configuration interfaces.

    """

    def __init__(self, game):
        self.game = game
        w, h = conf.WINSIZE
        w = int(0.5 * w)
        h = int(0.8 * h)
        Drawable.Layer.__init__(self, size=(w, h))
        GameLooper.__init__(self)

        self.sprites = self.addGroup(layer=self)

        self.events.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self._stop))

        self.set_background(color=BLACK)
        self.border(width=3, color=RED)
        s = Drawable.String(w=self, message='configuration',
                                fontSize=40)
        s.center(y=15)
        #print 1, s.get_position()
        s = Drawable.Stationary(w=self, sprite=s)
        s.draw()
        self.center()
        #print 2, self.get_position()

        q = Widget.SpriteTextButton(self, 'QUIT', callback=self._quit,
                                        group=self.events)
        q.center(y=50)
        self.sprites.add(q)

        cl = Widget.CloseButton(self, callback=self._stop,
                                        group=self.events)

        self.events.add(Event.KEYUP_Event(key=K_s, callback=self.save_config))
        save = Widget.SpriteTextButton(self, 'Save', callback=self.save_config,
                                        group=self.events)
        save.center(y=-50)
        self.sprites.add(save)

        self.show_video_modes()

    def show_video_modes(self):
        self.events.add(Event.KEYUP_Event(key=K_f, callback=self.toggle_fullscreen))
        self.events.add(Event.KEYUP_Event(key=K_PAGEUP, callback=self.grow))
        self.events.add(Event.KEYUP_Event(key=K_PAGEDOWN, callback=self.shrink))
        self.events.add(Event.KEYUP_Event(key=K_RETURN, callback=self._quit))

        s = Drawable.String(w=self, message='video',
                                fontSize=40)
        s.center(y=85)
        s = Drawable.Stationary(w=self, sprite=s)
        s.draw()

        b1 = Widget.SpriteTextButton(self, '640 x 480', callback=self.resize640x480,
                                        group=self.events)
        b1.center(y=125, dx=-100)
        self.sprites.add(b1)

        b2 = Widget.SpriteTextButton(self, '800 x 600', callback=self.resize800x600,
                                        group=self.events)
        b2.center(y=125)
        self.sprites.add(b2)

        b3 = Widget.SpriteTextButton(self, '1024 x 768', callback=self.resize1024x768,
                                        group=self.events)
        b3.center(y=125, dx=100)
        self.sprites.add(b3)

        b4 = Widget.SpriteTextButton(self, 'Full/Window', callback=self.toggle_fullscreen,
                                        group=self.events)
        b4.center(y=165)
        self.sprites.add(b4)

        self.pause()

    def grow(self, x=50, y=50):
        self.shrink(-x, -y)

    def shrink(self, x=50, y=50):
        """Resize the window (smaller)

        @param x: horizontal amount to reduce size
        @param y: vertical amount to reduce size

        """

        w, h = pygame.display.get_surface().get_size()
        w -= x
        h -= y
        self.window.resize((w, h))
        self.resize_reset()
        self.center()

    def resize640x480(self, arg=None):
        self.window.resize((640, 480))
        self.resize_reset()
        self.center()

    def resize800x600(self, arg=None):
        self.window.resize((800, 600))
        self.resize_reset()
        self.center()

    def resize1024x768(self, arg=None):
        self.window.resize((1024, 768))
        self.resize_reset()
        self.center()

    def toggle_fullscreen(self, arg=None):
        pygame.display.toggle_fullscreen()
        conf.WINFULL = not conf.WINFULL
        self.center()

    def resize_reset(self, arg=None):
        self.window = conf.window
        self.screen = self.window.screen
        self.bg = self.window.bg
        
        self.game.window = conf.window
        self.game.screen = self.game.window.screen
        self.game.bg = self.game.window.bg

        self.game.resize_reset()
        #self._window = self.game.window
        #self._window.screen = self._window.screen
        #self._window.bg = self._window.bg
        self.game.showMouse()
        self.game.freeMouse()

    def save_config(self, arg=None):
        import os
        import ConfigParser
        try:
            try:
                d = os.path.expanduser('~/.pygsear')
                os.listdir(d)
            except OSError:
                os.mkdir(d)
            
            f = os.path.expanduser('~/.pygsear/config')
            fd = file(f, 'w')
            c = ConfigParser.ConfigParser()
            c.add_section('screen')
            c.set('screen', 'WINWIDTH', conf.WINWIDTH)
            c.set('screen', 'WINHEIGHT', conf.WINHEIGHT)
            c.set('screen', 'WINFULL', conf.WINFULL)
            c.write(fd)
        except:
            self.beep()

    def pause(self):
        GameLooper.pause(self)
    
    def unpause(self):
        GameLooper.unpause(self)

    def loop(self):
        self.game.pause()
        mouse_visible = self.game.mouse_visible
        self.game.showMouse()
        mouse_grabbed = self.game.mouse_grabbed
        self.game.freeMouse()

        self.unpause()
        while not self.quit and not self.stop:
            self.sprites.clear()
            self.checkEvents()
            self.sprites.move()
            self.sprites.draw()
            self.udraw()

        self.pause()
        self.stop = 0
        if self.quit:
            self.game.quit = 1

        self.uclear()
        pygame.event.get()
        self.game.showMouse(mouse_visible)
        self.game.grabMouse(mouse_grabbed)
        self.game.unpause()


class Game(GameLooper):
    """The central game object.

    Classes which subclass this take part in the pygsear game
    framework and automatically get a splash screen, and the
    configuration interface.

    """

    splash_filename = 'pygsear_logo.png'

    def __init__(self, window=None):
        conf.game = self

        if window is None:
            if hasattr(conf, 'window'):
                window = conf.window
            else:
                window = Screen.Window()
        self.window = window
        self.screen = window.screen

        pygame.event.set_allowed(None)

        GameLooper.__init__(self)
        self.events.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self.configure))

        self.set_title()

        self.splash_screen()

        self.clock = pygame.time.Clock()
        conf.ticks = 0

        #pygame.event.set_allowed(None)

        self.showMouse()
        self.freeMouse()

        self.game_configuration = GameConfiguration(self)

        self.initialize()
        self.splash_screen_poof()
        self.window.clear()

    def splash_screen(self):
        """Show the splash screen

        Called as soon as window is created

        Game subclasses which do not want a splash screen can
        override this with a function that just does pass

        """

        if self.splash_filename:
            self._splash = self.addLayer(size=(200, 100))
            self._splash.center()

            title = Drawable.Image(w=self._splash, filename=self.splash_filename)
            title.center()
            title.udraw()

            self._splash.udraw()
        else:
            self._splash = None

    def splash_screen_poof(self):
        """Erase the splash screen

        Called at the end of __init__

        Game subclasses which do not want a splash screen should
        also override this with a function that just does pass

        """

        if self._splash is not None:
            self._splash.udraw()
            self.waitFor(timeout=2200)
            self._splash.uclear()

    def set_background(self, filename=None, img=None, tilename=None, tile=None, color=BLACK):
        """Set the background.

        @see: L{Screen.Layer}

        """
        self.window.set_background(filename, img, tilename, tile, color)
        self.bg = self.window.bg

    def set_title(self, title=None):
        if title is not None:
            pygame.display.set_caption(title)
        else:
            import sys
            title = sys.argv[0]
            self.set_title(title)

    def resize_reset(self):
        """Fix up the game after the screen has been resized
                
        """

        for sprite in self.sprites.sprites():
            if sprite is not self:
                sprite.kill()
        self.sprites.screen = self.window.screen
        self.sprites.bg = self.window.bg

        self.events.kill()
        self.events.add(Event.QUIT_Event(callback=self._quit))
        self.events.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self.configure))

        self.initialize()

    def showMouse(self, show=1):
        """Show the mouse cursor
        
        @param show: 1 yes show or 0 no hide
        
        """

        self.mouse_visible = show
        pygame.mouse.set_visible(show)

    def hideMouse(self, hide=1):
        """Hide the mouse cursor
        
        @param hide: 1 yes hide or 0 no show
        
        """

        self.showMouse(not hide)

    def grabMouse(self, grab=1):
        """Capture all  mouse and keyboard input
        
        Also keeps mouse locked inside of window.
        
        @param grab: 1 yes grab or 0 no release
        
        """

        self.mouse_grabbed = grab
        pygame.event.set_grab(grab)

    def freeMouse(self, free=1):
        """Stop capturing all input
        
        @param free: 1 yes release or 0 no grab
        
        """

        self.grabMouse(not free)

    def update(self, areas=None):
        """update the display
                
        @param areas: rect or list of rects to update
        
        """

        if areas is None:
            pygame.display.update()
        else:
            pygame.display.update(areas)

    def waitFor(self, key=K_RETURN, timeout=None):
        """Pause the game, waiting for a keystroke.
        
        Still allows the game to be ended by clicking the
        window close button.
        
        """

        self.pause()

        if timeout is not None:
            startTime = pygame.time.get_ticks()
        clearQ = pygame.event.get()

        group = Event.EventGroup()
        group.add(Event.QUIT_Event(callback=self._quit))
        group.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self.configure))
        group.add(Event.KEYUP_Event(key=key, callback=self._stop))

        self.stop = 0
        while not self.quit and not self.stop:
            if timeout is not None:
                timeNow = pygame.time.get_ticks()
                if timeNow - startTime >= timeout:
                    self.stop = 1
            group.check()
        self.stop = 0
        
        self.unpause()

    def playAgain(self):
        """Ask if player wants to play again.
        
        """

        againMsg = Drawable.String(message='Press [ENTER] to Play Again',
                                fontSize=60, color=LGREEN)
        againMsg.center()
        againMsg.nudge(dy=40)
        self.againMsg = Drawable.Stationary(sprite=againMsg)
        self.againMsg.draw()

        self.waitFor()
        if not self.quit:
            self.againMsg.clear()
            self.overMsg.clear()
            self.restart()

    def gameOver(self):
        """Show a Game Over message.
        
        """

        overMsg = Drawable.String(self.window, 'Game Over', fontSize=60, color=LBLUE)
        overMsg.center()
        self.overMsg = Drawable.Stationary(self.window, overMsg)
        self.overMsg.draw()
        pygame.display.update()
        pygame.time.wait(1500)
        self.playAgain()        

    def restart(self):
        self.sprites.kill()
        self.events.kill()
        self.events.add(Event.QUIT_Event(callback=self._quit))
        self.events.add(Event.KEYUP_Event(key=K_ESCAPE, callback=self.configure))
        self.initialize()

    def initialize(self):
        """Further initialization
        
        Most games will create their main objects here.
        
        """

        self.set_background()

    def mainloop(self, frames=0):
        """The main game loop.
        
        @param frames: number of times to loop
            Defaults to C{0}, which means loop until the game is over.

        """

        while not self.quit:
            frame = 0
            while not self.quit and not self.stop and (frame < frames or not frames):
                conf.ticks = self.clock.tick(conf.MAX_FPS)
                self.sprites.clear()
                self.checkEvents()
                self.sprites.move()
                self.checkCollisions()
                if self.layers:
                    for layer in self.layers:
                        layer.updateContents()
                dirty = self.sprites.draw()
                #print 'dirty', dirty
                pygame.display.update(dirty)
                #self.update(dirty)
                frame += 1

            if not frames and not self.quit:
                self.gameOver()
            else:
                break

    def step(self):
        """Take one trip through the mainloop"""

        self.mainloop(1)

    def configure(self, pygame_event, **kwargs):
        """Bring up the configuration screen"""

        self.game_configuration.loop()

    def unpause(self):
        GameLooper.unpause(self)
        self.clock.tick()


class TwistedGame(Game):
    """Alternate central game object using Twisted event loop"""

    def __init__(self, window=None, reactor=None, delay=0.05):
        if reactor is None:
            pass
            #raise TypeError
        else:
            self.reactor = reactor
        self.delay = delay
        self.dirty = []
        Game.__init__(self, window)

    def checkGameOver(self):
        if self.quit:
            print 'quitting'
            self.reactor.stop()
            os._exit(1)

    def mainloop(self):
        """The main twisted game loop."""

        conf.ticks = self.clock.tick(conf.MAX_FPS)
        self.sprites.clear()
        self.checkEvents()
        self.checkGameOver()
        self.sprites.move()
        self.checkCollisions()
        dirty = self.sprites.draw()
        self.update(dirty)
        self.reactor.callLater(self.delay, self.mainloop)




