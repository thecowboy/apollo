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

from zmq.eventloop.ioloop import IOLoop

from tornado.options import options

from apollo.server.models import meta
from apollo.server.models.auth import Session

from apollo.server.protocol.packet import ORIGIN_INTER
from apollo.server.protocol.packet.meta import deserializePacket

class Consumer(object):
    def __init__(self, handler):
        self.handler = handler

        self.subscriber = handler.application.bus.zmqctx.socket(zmq.SUB)
        self.subscriber.connect(urlparse.urlunsplit((
            options.zmq_transport,
            options.zmq_host,
            "",
            "",
            ""
        )))

        self.session = meta.session.find(Session, { "token" : handler.token }).one()

        # subscribe to session channel
        self.subscribe("ex.session.%s" % self.session._id)

        logging.debug("Created subscriber for %s" % self.session._id)

    def eat(self):
        """
        Begin consuming events.
        """
        if self.session.getUser():
            self.userSubscribe()
        IOLoop.instance().add_handler(self.subscriber, lambda *args: self.on_message(self.subscriber), zmq.POLLIN)

    def userSubscribe(self):
        """
        Subscribe to the user specific channels.
        """
        user = self.session.getUser()
        self.subscribe("ex.user.*")
        self.subscribe("ex.user.%s" % user._id)
        self.subscribe("ex.loc.%s" % user.location_id)

    def subscribe(self, channel):
        self.subscriber.setsockopt(zmq.SUBSCRIBE, channel)

    def unsubscribe(self, channel):
        self.subscriber.setsockopt(zmq.UNSUBSCRIBE, channel)

    def shutdown(self):
        """
        Shut down the consumer.
        """
        logging.debug("Shutting down consumer for %s" % self.session._id)
        IOLoop.instance().remove_handler(self.subscriber)
        self.subscriber.close()

    def on_message(self, socket):
        """
        Handle a message.

        :Parameters:
             * ``socket``
                Socket message arrives on.
        """
        message = socket.recv()
        logging.debug("Got raw message: %s" % message)
        packet, payload = message.split(":", 1)

        logging.debug("Sending user message packet: %s" % message)
        self.handler.finish(payload)

        # shut down now, because we most definitely don't want any more stuff
        self.shutdown()
