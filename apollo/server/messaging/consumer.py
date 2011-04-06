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

import uuid

from apollo.server.models import meta
from apollo.server.models.auth import Session

class Consumer(object):
    """
    Consumer object. These are actually one-time use only.
    """

    def __init__(self, handler):
        self.handler = handler

        self.bus = handler.application.bus
        self.channel = self.bus.channel
        self.ctag = uuid.uuid4().hex

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

        self.channel.basic_consume(
            consumer_callback=self.on_message,
            queue="ex-%s" % self.session._id,
            no_ack=False,
            consumer_tag=self.ctag
        )

        logging.debug("Created subscriber for %s" % self.session._id)

    def shutdown(self):
        """
        Shut down the consumer.
        """
        self.rejecting = True

        logging.debug("Shutting down consumer for %s" % self.session._id)
        self.channel.basic_cancel(consumer_tag=self.ctag)

    def on_message(self, channel, method, header, body):
        """
        Handle a message.
        """
        logging.debug("Got packet: %s" % body)

        if self.rejecting:
            logging.info("Rejecting packet: %s" % body)
            channel.basic_reject(delivery_tag=method.delivery_tag)
            return

        channel.basic_ack(delivery_tag=method.delivery_tag)
        prefixparts = method.routing_key.split(".")

        if prefixparts[0] != "ex":
            # this is not an ex frame
            return

        try:
            self.handler.finish(body)
        except IOError:
            logging.warn("Dropped packet due to closed request: %s" % body)

        # shut down now, because we most definitely don't want any more stuff
        # (but we tend to get stuff anyway, which is why we have a rejecting
        # field)
        self.shutdown()
