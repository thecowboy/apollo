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

from tornado.ioloop import IOLoop

from apollo.server.models import meta
from apollo.server.models.auth import Session

class Consumer(object):
    """
    Consumer object. These are actually one-time use only.
    """

    def __init__(self, handler):
        self.handler = handler
        self.io_loop = IOLoop.instance()

        self.bus = handler.application.bus
        self.rejecting = False

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
        self.subscribe("ex.session.%s" % self.session._id)

        logging.debug("Created subscriber for %s" % self.session._id)

        if self.session.getUser():
            self.userSubscribe()

    def userSubscribe(self):
        """
        Subscribe to the user specific channels.
        """
        user = self.session.getUser()
        self.subscribe("ex.user.global")
        self.subscribe("ex.user.%s" % user._id)
        self.subscribe("ex.loc.%s" % user.location_id)

    def subscribe(self, channel):
        self.bus.subscribe(channel, "ex-%s" % self.session._id, self.on_message)

    def unsubscribe(self, channel):
        self.bus.unsubscribe(channel, "ex-%s" % self.session._id)

    def shutdown(self):
        """
        Shut down the consumer.
        """
        logging.debug("Shutting down consumer for %s" % self.session._id)
        self.bus.unconsume(self.ctag)

    def on_message(self, ctag, method, header, body):
        """
        Handle a message.
        """
        self.ctag = ctag

        if self.rejecting:
            logging.info("Rejecting packet: %s" % body)
            self.bus.channel.basic_reject(delivery_tag=method.delivery_tag)
            return

        self.rejecting = True
        prefixparts = method.routing_key.split(".")

        if prefixparts[0] != "ex":
            # this is not an ex frame
            return

        try:
            self.handler.finish(body)
        except IOError:
            logging.warn("Dropped packet due to closed request: %s" % body)

        # shut down now, because we most definitely don't want any more stuff
        self.shutdown()
