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


"""Objects used for network communication using Twisted

More information available at http://twistedmatrix.com/

"""

try:
    import twisted
except ImportError:
    import Widget

    msg = """Game requires Twisted Python for networking
    see  http://twistedmatrix.com/  for information"""
    dlg = Widget.Dialog_OK(message=msg)
    dlg.modal()
    raise ImportError, "Error importing twisted modules"

from twisted.internet import reactor
from twisted.spread import pb


class TwoPlayerConnection(pb.Root, pb.Referenceable):
    """Simple two player network connector

    First tries to connect to an existing server, and if none is
    found, will then wait for an incoming connection.

    """

    def __init__(self, game):
        self.game = game
        self.makeConnection()

    def makeConnection(self):
        """Try to connect to an existing server."""

        print 'Client: connecting'
        pb.getObjectAt(self.game.host, self.game.port, 10).addCallbacks(self.gotObject, self.gotNoObject)

    def gotObject(self, connection):
        """If server exists, and contact is made."""

        print 'Client: server contacted'
        connection.callRemote("give_connection", self).addCallbacks(self.got_connection, self.gotNoObject)

    def gotNoObject(self, reason):
        """If no server answers, then start one."""

        print 'Client: no server found'
        self.startListening()

    def startListening(self):
        """Start a server, and wait for a connection attempt."""

        print 'No server found. Listening for connections'
        reactor.listenTCP(self.game.port, pb.BrokerFactory(self))

    def remote_give_connection(self, connection):
        """Server gets client's Connection, and returns it's own Connection
        to client.

        """

        self.connection = connection
        print 'Server: got connection '
        return self

    def got_connection(self, connection):
        """Client gets server's connection."""

        self.connection = connection
        print 'Client: got connection '
