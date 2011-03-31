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

import logging
import urlparse

from tornado.options import options

from pymongo.objectid import ObjectId

import zmq
from zmq.eventloop.ioloop import IOLoop

from apollo.server.component import Component

from apollo.server.protocol.packet import ORIGIN_INTER
from apollo.server.protocol.packet.meta import deserializePacket

from apollo.server.models import meta
from apollo.server.models.auth import Session, User

class Bus(Component):
    """
    Apollo's message bus system.
    """
    def __init__(self, core):
        super(Bus, self).__init__(core)
        self.zmqctx = zmq.Context()
        self.publisher = self.zmqctx.socket(zmq.PUB)
        self.publisher.bind(urlparse.urlunsplit((
            options.zmq_transport,
            options.zmq_host,
            "",
            "",
            ""
        )))
        self.consumer = self.zmqctx.socket(zmq.SUB)
        self.consumer.connect(urlparse.urlunsplit((
            options.zmq_transport,
            options.zmq_host,
            "",
            "",
            ""
        )))
        self.consumer.setsockopt(zmq.SUBSCRIBE, "inter")
        IOLoop.instance().add_handler(self.consumer, lambda *args: self.on_inter_message(self.consumer), zmq.POLLIN)

    def broadcast(self, dest, packet):
        """
        Broadcast a packet to a specific destination.

        :Parameters:
             * ``dest``
               Destination. Prefixed with ``cross.`` for cross-server
               communication and ``user.`` for direct user messaging.

             * ``packet``
               Packet to broadcast.
        """
        logging.debug("Sending to %s: %s" % (dest, packet.dump()))
        self.publisher.send("%s:%s" % (dest, packet.dump()))

    def on_inter_message(self, socket):
        """
        Process an "inter" message.
        """
        message = socket.recv()
        prefix, payload = message.split(":", 1)
        prefixparts = prefix.split(".")
        packet = deserializePacket(payload)
        packet._origin = ORIGIN_INTER

        if prefixparts[1] == "user":
            for session in meta.session.find(Session, { "user_id" : ObjectId(prefixparts[2]) }):
                packet.dispatch(self.core, session)
        elif prefixparts[1] == "loc":
            for user in meta.session.find(User, { "location_id" : ObjectId(prefixparts[2]) }):
                for session in meta.session.find(Session, { "user_id" : user._id }):
                    packet.dispatch(self.core, session)
