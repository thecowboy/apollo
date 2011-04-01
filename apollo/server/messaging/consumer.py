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

from tornado.ioloop import IOLoop

from tornado.options import options

from apollo.server.models import meta
from apollo.server.models.auth import Session

from apollo.server.protocol.packet import ORIGIN_INTER
from apollo.server.protocol.packet.meta import deserializePacket

class Consumer(object):
    def __init__(self, handler):
        self.handler = handler
        self.io_loop = IOLoop.instance()
        self.subscriptions = []

        self.bus = handler.application.bus

    def eat(self):
        """
        Begin consuming events.
        """
        try:
            self.session = meta.session.find(Session, { "token" : self.handler.token }).one()
        except ValueError:
            logging.warn("Session %s does not exist; bailing" % self.handler.token)
            return

        # subscribe to session queue
        self.subscribe("/queue/ex.session.%s" % self.session._id)

        self.bus.registerHandler(self.on_message)

        logging.debug("Created subscriber for %s" % self.session._id)

        if self.session.getUser():
            self.userSubscribe()

    def userSubscribe(self):
        """
        Subscribe to the user specific channels.
        """
        user = self.session.getUser()
        self.subscribe("/topic/ex.user.*")
        self.subscribe("/queue/ex.user.%s" % user._id)
        self.subscribe("/topic/ex.loc.%s" % user.location_id)

    def subscribe(self, channel):
        # don't resubscribe or anything
        if self.bus.isSubscribed(channel):
            self.subscriptions.append(channel)
        self.bus.subscribe(channel)

    def unsubscribe(self, channel):
        self.bus.unsubscribe(channel)

    def shutdown(self):
        """
        Shut down the consumer.
        """
        logging.debug("Shutting down consumer for %s" % self.session._id)
        self.bus.unregisterHandler(self.on_message)
        for subscription in self.subscriptions:
            self.bus.unsubscribe(subscription)

    def on_message(self, frame):
        """
        Handle a message.

        :Parameters:
             * ``frame``
                Frame received.
        """

        payload = frame.body
        prefix = frame.headers["destination"]
        dummy, destSpec, dest = prefix.split("/", 2)
        prefixparts = dest.split(".")

        if prefixparts[0] != "ex":
            # this is not an ex frame
            return

        try:
            self.handler.finish(payload)
        except IOError:
            logging.warn("Dropped packet due to closed request: %s" % payload)

        # shut down now, because we most definitely don't want any more stuff
        self.shutdown()
