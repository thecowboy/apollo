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

import zmq

class Bus(object):
    """
    Apollo's message bus system.
    """
    def __init__(self, core):
        self.zmqctx = zmq.Context()
        self.publisher = self.zmqctx.socket(zmq.PUB)
        self.publisher.bind(urlparse.urlunsplit((
            options.zmq_transport,
            options.zmq_host,
            "",
            "",
            ""
        )))

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
