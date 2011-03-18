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

class Channel(object):
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus
        self.transports = {}

    def subscribeTransport(self, transport):
        self.transports[transport.token] = transport
        logging.debug("Currently attached transports on %s: %s" % (self.name, self.transports.keys()))

    def unsubscribeTransport(self, transport):
        del self.transports[transport.token]
        # FIXME: why does this cause weird things to happen?!
        #if not self.transports:
        #    self.bus.shutdownChannel(self.name)
        logging.debug("Currently attached transports on %s: %s" % (self.name, self.transports.keys()))

    def processEvent(self, event):
        for transport in self.transports.values():
            event.dispatch(transport, self.bus.core)

    def sendEvent(self, event):
        for transport in self.transports.values():
            transport.sendEvent(event)
