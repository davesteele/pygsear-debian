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

from twisted.internet import gtkreactor
gtkreactor.install()

import gtk

from twisted.internet import reactor

import pygsear
import pygsear.Game

class PygameGtkWindow(gtk.GtkWindow):
    def __init__(self):
        w = gtk.GtkWindow(gtk.WINDOW_TOPLEVEL)
        w.set_default_size(250, 400)
        w.connect('destroy', self.quit)

        vb = gtk.GtkVBox()
        w.add(vb)

        b = gtk.GtkButton('QUIT')
        b.signal_connect('clicked', self.quit)
        vb.add(b)

        self.sta = gtk.GtkButton('START GAME')
        self.sta.signal_connect('clicked', self.start)
        vb.add(self.sta)

        self.login = gtk.GtkButton('show login')
        self.login.signal_connect('clicked', self.show_login)
        vb.add(self.login)

        self.sto = gtk.GtkButton('')
        self.sto.signal_connect('clicked', self.stop)
        vb.add(self.sto)

        w.show_all()
        self.w = w

        reactor.callLater(0.5, self.check_stuff)

    def set_game(self, game):
        self.game = game

    def start(self, b):
        if not hasattr(self, 'game'):
            print 'starting', b
            game = TG(reactor=reactor, delay=0.05)
            self.set_game(game)
            b["label"] = "STARTED"
            game.mainloop()
        else:
            print 'game already started'

    def show_login(self, b):
        if hasattr(self, 'game'):
            if not self.game.sprites.has(self.game.dlg):
                self.game.show_login()

    def stop(self, d):
        if not hasattr(self, 'game'):
            print 'game not started yet'
            return
        self.game.stopStart(self.game.b2)
        if self.game.b2.moving:
            self.sto["label"] = 'STOP BUTTON'
            print 'starting', d
        else:
            self.sto["label"] = 'START BUTTON'
            print 'stopping', d
        self.w.hide()
        reactor.callLater(5, self.show)

    def check_stuff(self):
        if hasattr(self, 'game'):
            if self.game.b2.moving:
                self.sto["label"] = 'STOP BUTTON'
            else:
                self.sto["label"] = 'START BUTTON'

            if self.game.sprites.has(self.game.dlg):
                self.login["label"] = 'showing login'
            else:
                self.login["label"] = 'show login'

        reactor.callLater(0.1, self.check_stuff)
        

    def show(self):
        self.w.show()

    def quit(self, b):
        gtk.mainquit()

class TG(pygsear.Game.TwistedGame):
    def initialize(self):
        self.set_background(tilename='bg9.png')

        sky = pygsear.Drawable.Image(self.window, 'sky.png')
        b2 = pygsear.Widget.SpriteButton(sprite=sky, group=self.events)
        p = pygsear.Path.CirclePath(duration=20)
        p.set_loop(-1)
        b2.set_path(p)
        b2.moving = 1
        self.b2 = b2
        b2.set_callback(self.stopStart)
        self.sprites.add(b2)
        self.sky = b2

        self.show_login()

    def show_login(self, ev=None):
        self.dlg = pygsear.Widget.Dialog_LineInput(self.window, message='Username:',
                                callback=self.get_username, group=self.events)
        self.sprites.add(self.dlg)

    def get_username(self, text):
        print 'username is', text

    def stopStart(self, ev=None):
        if not hasattr(self.sky, 'savedPath'):
            self.sky.savedPath = self.sky.path
            self.sky.savedPath.pause()
            self.sky.set_path(pygsear.Path.StationaryPath(self.sky))
            self.sky.move()
        else:
            path = self.sky.path
            path.pause()
            self.sky.savedPath.unpause()
            self.sky.set_path(self.sky.savedPath)
            self.sky.savedPath = path
        if self.sky.moving:
            self.sky.moving = 0
        else:
            self.sky.moving = 1


def main():
    gp = PygameGtkWindow()

    # Need to set delay to something other than 0
    # (at least on slower systems)
    # Otherwise the gtk pieces never get updated

    reactor.run()

if __name__ == '__main__':
    main()
