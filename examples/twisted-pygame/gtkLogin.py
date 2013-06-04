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

import gtk

class LoginInfo:
    def __init__(self):
        self.username = 'guest'
        self.password = 'guest'
        self.host = 'localhost'
        self.port = 8888

        self.quit = 0

class LoginWindow(gtk.GtkWindow):
    def __init__(self, info):
        self.info = info

        w = gtk.GtkWindow(gtk.WINDOW_TOPLEVEL)
        #w.set_default_size(250, 400)
        w.connect('destroy', self.quit)

        vb = gtk.GtkVBox()
        w.add(vb)

        b = gtk.GtkButton('QUIT')
        b.signal_connect('clicked', self.quit)
        vb.add(b)

        t = gtk.GtkTable(2, 4)

        row = 0
        for label in [ 'username', 'password', 'host', 'port']:
            entryName = label+'Entry'
            entry = gtk.GtkEntry()
            text = getattr(self.info, label)
            entry.set_text(str(text))
            entry.signal_connect('activate', self.login)
            setattr(self, entryName, entry)

            fieldLabel = label.capitalize() + ':'
            l = gtk.GtkLabel(fieldLabel)

            t.attach(l, 0, 1, row, row+1)
            t.attach(entry, 1, 2, row, row+1)
            row += 1

        vb.add(t)

        def dike():
            self.usernameEntry = gtk.GtkEntry()
            self.usernameEntry.set_text(self.info.username)
            self.usernameEntry.signal_connect('activate', self.login)
            vb.add(self.usernameEntry)

            self.passwordEntry = gtk.GtkEntry()
            self.passwordEntry.set_text(self.info.password)
            self.passwordEntry.signal_connect('activate', self.login)
            vb.add(self.passwordEntry)

            self.hostEntry = gtk.GtkEntry()
            self.hostEntry.set_text(self.info.host)
            self.hostEntry.signal_connect('activate', self.login)
            vb.add(self.hostEntry)

            self.portEntry = gtk.GtkEntry()
            self.portEntry.set_text(str(self.info.port))
            self.portEntry.signal_connect('activate', self.login)
            vb.add(self.portEntry)

        b = gtk.GtkButton('LOGIN')
        b.signal_connect('clicked', self.login)
        vb.add(b)

        w.show_all()

        self.w = w

    def login(self, b):
        self.info.username = self.usernameEntry.get_text()
        self.info.password = self.passwordEntry.get_text()
        self.info.host = self.hostEntry.get_text()
        self.info.port = int(self.portEntry.get_text())
        self.w.hide()
        gtk.mainquit()

    def quit(self, b):
        self.info.quit = 1
        gtk.mainquit()

