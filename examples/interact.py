#!/usr/bin/env python

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


import os

import pygame
from pygame.locals import K_ESCAPE, K_F1, K_F2, K_F8

from pygsear import Event
from pygsear.Widget import Console, Dialog_LineInput, Dialog_OK
from pygsear.locals import BLACK, WHITE, GRAY, LGRAY, RED, BLUE, GREEN, YELLOW
from pygsear.locals import ORANGE, PURPLE, LRED, LGREEN, LBLUE, DRED, DBLUE, DGREEN
from pygsear import conf

from penguin_demos import Penguin



class InteractPenguin(Penguin):
    def shrink(self, dx=50, dy=50):
        Penguin.shrink(self, dx, dy)
        w, h = interpreter.size
        w -= 50
        h -= 25
        interpreter.resize((w, h))
        interpreter.set_modal_events()

    def grow(self, dx=50, dy=50):
        Penguin.grow(self, dx, dy)
        w, h = interpreter.size
        w += 50
        h += 25
        interpreter.resize((w, h))
        interpreter.set_modal_events()


class TurtleConsole(Console):
    def __init__(self, locals, size):
        self.clock = pygame.time.Clock()
        Console.__init__(self, locals, size)

    def set_session_file(self):
        #dot = os.path.abspath('.')
        #suggested_file = os.path.join(dot, 'penguin_session.py')
        session_file = Dialog_LineInput(message='Session File', default='penguin_session.py').modal()

        if session_file is not None:
            self.session_file = session_file
        return session_file

    def save_session(self, ev):
        if not hasattr(self, 'session_file') or self.session_file is None:
            session_file = self.set_session_file()
            if session_file is not None:
                if os.path.exists(session_file):
                    self.events.disable()
                    dlg = Dialog_OK(message='File exists.  Overwrite?').modal()
                    if dlg is None:
                        self.line.udraw()
                        self.layer.udraw()
                        if hasattr(self, 'session_file'):
                            del(self.session_file)

                    self.events.enable()

        if not hasattr(self, 'session_file'):
            self.new_line('save cancelled')
            return

        f = file(self.session_file, 'w')
        for line in self.history:
            f.write(line)
            f.write('\n')
        f.close()
        if self.locals['pete'].visible:
            self.locals['pete'].udraw()
        self.new_line('functions saved')

    def load_session(self, ev):
        if not hasattr(self, 'session_file') or self.session_file is None:
            session_file = self.set_session_file()

        if session_file is not None:
            try:
                f = file(session_file)
            except IOError:
                self.new_line('File not found.')
                self.session_file = None
            else:
                if session_file is not None:
                    loading = 0
                    for line in f:
                        line = line.strip('\n')
                        if line.startswith('def') or line.startswith('class'):
                            if loading:
                                self.run_command('')
                            loading = 1
                            self.run_command(line)
                        elif loading:
                            if line.startswith(' '):
                                self.run_command(line)
                        else:
                            loading = 0
                    self.run_command('')

        if self.locals['pete'].visible:
            self.locals['pete'].udraw()

    def deactivate(self):
        Console.deactivate(self)
        if self.locals['pete'].visible:
            self.locals['pete'].udraw()

    def set_modal_events(self):
        self.quit_ev = Event.QUIT_Event(callback=self._quit)
        self.events.add(self.quit_ev)
        self.stop_ev = Event.KEYUP_Event(key=K_ESCAPE, callback=self.toggle_visible)
        self.events.add(self.stop_ev)
        save_sess = Event.KEYUP_Event(key=K_F1, callback=self.save_session)
        self.events.add(save_sess)
        load_sess = Event.KEYUP_Event(key=K_F2, callback=self.load_session)
        self.events.add(load_sess)
        quit_ev2 = Event.KEYUP_Event(key=K_F8, callback=self._quit)
        self.events.add(quit_ev2)

    def greeting(self):
        self.new_line('Press ESC to show/hide console')
        self.new_line('Press F8 to QUIT')
        self.new_line('')
        self.new_line('Press F1 to save functions')
        self.new_line('Press F2 to load functions')

    def modal(self):
        self.activate()

        self.greeting()
        self.set_modal_events()

        self.line.udraw()

        self.stop = 0
        while not self.stop:
            conf.ticks = min(20, self.clock.tick(conf.MAX_FPS))

            self.layer.clear()
            self.events.check()
            if self.active:
                if self.locals['pete'].visible:
                    self.locals['pete'].udraw()
                self.line.udraw()
                self.layer.udraw()

            if not self.line.repeater.key_held:
                ev = pygame.event.wait()
                pygame.event.post(ev)

        self.quit_ev.kill()
        self.stop_ev.kill()
        self.layer.uclear()

        self.deactivate()


if __name__ == '__main__':
    pete = InteractPenguin()

    loc = {'pete': pete,

        'forward': pete.forward,
        'backward': pete.backward,
        'right': pete.right,
        'left': pete.left,

        'home': pete.home,
        'reset': pete.reset,
        'refresh': pete.refresh,
        'clearScreen': pete.clearScreen,
        'cls': pete.clearScreen,
        'hide': pete.hide,
        'show': pete.show,

        'write': pete.write,
        'circle': pete.circle,
        'cCircle': pete.cCircle,
        'turnTo': pete.turnTo,

        'penUp': pete.penUp,
        'penDown': pete.penDown,
        'set_color': pete.set_color,

        'shrink': pete.shrink,
        'grow': pete.grow,

        'begin': pete.begin,
        'commit': pete.commit,
        'rollback': pete.rollback,

        'BLACK': BLACK,
        'WHITE': WHITE,
        'GRAY': GRAY,
        'LGRAY': LGRAY,
        'RED': RED,
        'BLUE': BLUE,
        'GREEN': GREEN,
        'YELLOW': YELLOW,
        'ORANGE': ORANGE,
        'PURPLE': PURPLE,
        'LRED': LRED,
        'LGREEN': LGREEN,
        'LBLUE': LBLUE,
        'DRED': DRED,
        'DBLUE': DBLUE,
        'DGREEN': DGREEN,
    }

    pygame.event.set_allowed(None)


    interpreter = TurtleConsole(locals=loc, size=(700, 250))

    interpreter.modal()
