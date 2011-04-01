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

import uuid
import logging

from tornado.options import options
from tornado.ioloop import IOLoop

from stompy import Stomp

from pymongo.objectid import ObjectId

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

        self.pubsub = Stomp(options.stomp_host, options.stomp_port)
        self.pubsub.connect(options.stomp_username, options.stomp_password, uuid.uuid4().hex)

        self.subscribe("/topic/inter.>")
        self.io_loop = IOLoop.instance()

        self.handlers = []

        self.registerHandler(self.on_inter_message)
        self.io_loop.add_handler(self.pubsub.sock.fileno(), lambda *args: self.fireHandlers(), IOLoop.READ)

    def subscribe(self, dest):
        self.pubsub.subscribe({
            "destination"   : dest,
            "ack"           : "client"
        })

    def unsubscribe(self, dest):
        self.pubsub.unsubscribe({
            "destination"   : dest
        })

    def isSubscribed(self, dest):
        return self.pubsub._subscribed_to.get(dest, False)

    def registerHandler(self, handler):
        """
        Register a handler for IOLoop.
        """
        self.handlers.append(handler)

    def unregisterHandler(self, handler):
        """
        Unregister a handler.
        """
        self.handlers.remove(handler)
        
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
        self.pubsub.send({
            "destination"   : dest,
            "body"          : packet.dump(),
            "persistent"    : True
        })

    def fireHandlers(self):
        frame = self.pubsub.receive_frame(nonblocking=True)

        if frame is None:
            return

        for handler in self.handlers:
            handler(frame)

    def on_inter_message(self, frame):
        """
        Process an "inter" message.
        """
        payload = frame.body
        prefix = frame.headers["destination"]
        dummy, destSpec, dest = prefix.split("/", 2)
        prefixparts = dest.split(".")

        if prefixparts[0] != "inter":
            # this is not an inter frame
            return

        packet = deserializePacket(payload)
        packet._origin = ORIGIN_INTER

        if prefixparts[1] == "user":
            for session in meta.session.find(Session, { "user_id" : ObjectId(prefixparts[2]) }):
                packet.dispatch(self.core, session)
        elif prefixparts[1] == "loc":
            for user in meta.session.find(User, { "location_id" : ObjectId(prefixparts[2]) }):
                for session in meta.session.find(Session, { "user_id" : user._id }):
                    packet.dispatch(self.core, session)
