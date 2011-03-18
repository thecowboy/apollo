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
import zmq

#from tornado.ioloop import IOLoop
from zmq.eventloop.ioloop import IOLoop

from tornado.options import options

from apollo.server.protocol.packet.meta import deserialize_packet

class Consumer(object):
    def __init__(self, bus, transport):
        self.bus = bus
        self.transport = transport

        self.subscriber = self.bus.zmqctx.socket(zmq.SUB)
        self.subscriber.connect(urlparse.urlunsplit((
            options.zmq_transport,
            options.zmq_host,
            "",
            "",
            ""
        )))

        # subscribe to user channel
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "user.*")
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "user.%s" % transport.session().getUser()["_id"])

        # subscribe to cross channel
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "cross.*")
        self.subscriber.setsockopt(zmq.SUBSCRIBE, "cross.%s" % transport.session().getUser()["_id"])

        logging.debug("Created subscriber")

        IOLoop.instance().add_handler(self.subscriber, lambda *args: self.on_message(self.subscriber), zmq.POLLIN)

    def shutdown(self):
        logging.debug("Shutting down consumer for %s" % self.transport)
        IOLoop.instance().remove_handler(self.subscriber)
        self.subscriber.close()

    def on_message(self, socket):
        message = socket.recv()
        logging.debug("Got raw message: %s" % message)

        prefix, payload = message.split(":", 1)
        prefixparts = prefix.split(".")

        if prefixparts[0] == "cross":
            self.on_cross_message(payload)
        elif prefixparts[0] == "user":
            self.on_user_message(payload)

    def on_cross_message(self, message):
        logging.debug("Sending cross message packet: %s" % message)
        deserialize_packet(message).dispatch(self.transport, self.transport.core)

    def on_user_message(self, message):
        logging.debug("Sending user message packet: %s" % message)
        self.transport.sendEvent(deserialize_packet(message))
