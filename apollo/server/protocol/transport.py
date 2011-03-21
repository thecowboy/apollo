#
# Copyright (C) 2011 by Tony Young
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
Transport communication for the Apollo protocol.
"""

import logging

import os
from hashlib import sha256

from apollo.server.component import Component

from apollo.server.models import meta
from apollo.server.models.session import Session

from apollo.server.protocol.packet.packetlogout import PacketLogout

from apollo.server.messaging.consumer import Consumer

class Transport(Component):
    """
    Transport. Has a socket-like interface to hide the fact connections are not
    persistent. Also has a consumer for reading messages off a message queue
    and records its own session.
    """

    def __init__(self, core, bound_handler=None):
        super(Transport, self).__init__(core)
        self.bound_handler = bound_handler

        session = Session()
        self.token = session.token
        meta.session.save(session)
        meta.session.flush()

        self.nonce = sha256(os.urandom(64)).hexdigest()
        self.intermedq = []
        self.consumer = None

    def consume(self):
        """
        Start consuming messages from the message queue.
        """
        self.consumer = Consumer(self.core.bus, self)

    def bind(self, bind):
        """
        Bind a handler to this socket.

        :Parameters:
            * ``bind``
              Handler to bind.
        """
        self.bound_handler = bind
        logging.debug("Binding %s: %s" % (self, bind))
        to_send = self.intermedq[:]
        self.intermedq = []

        for packet in to_send:
            self.sendEvent(packet)

    def sendEvent(self, packet):
        """
        Send a packet.

        :Parameters:
            * ``packet``
              Packet to send.
        """
        if self.bound_handler is None:
            logging.debug("Packet placed on intermediate queue: %s" % packet)
            logging.debug(self.core.connections)
            self.intermedq.append(packet)
            return

        logging.debug("Sending packet: %s" % packet)
        self.bound_handler.send(packet)

        # unbind immediately
        self.bound_handler = None

    def session(self):
        """
        Get the session object from the database.
        """
        return meta.session.find(Session, { "token" : self.token }).one()

    def shutdown(self, msg=None):
        """
        Shutdown the transport.

        :Parameters:
            * ``msg``
              Optional message to provide.
        """
        msg = msg or "Unknown reason"

        if self.consumer is not None:
            self.consumer.shutdown()

        user = self.session().getUser()
        if user is not None:
            self.sendEvent(PacketLogout(msg=msg))
            self.core.bus.broadcast("user.*", PacketLogout(username=user.name, msg=msg))
            user.online = False

        meta.session.remove(Session, { "token" : self.token })

        meta.session.flush_all()

        self.core.loseTransport(self.token)

    def __repr__(self):
        return "<Transport (%s): %s>" % (
            self.bound_handler is None and "unbound" or "bound",
            self.token
        )
