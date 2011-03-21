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

import json

import logging

from tornado.options import options
from tornado.web import RequestHandler, asynchronous, HTTPError

from apollo.server.models import meta
from apollo.server.models.session import Session

from apollo.server.protocol.transport import Transport
from apollo.server.protocol.packet.meta import deserialize_packet
from apollo.server.protocol.packet.packeterror import PacketError

"""
Apollo's HTTP frontend handlers.
"""

class FrontendHandler(RequestHandler):
    """
    Send the user the Apollo client frontend.
    """

    def get(self):
        self.set_header("Content-Type", "text/html; charset=utf8")
        self.write(self.application.loader.load("frontend.html").generate())

class SessionHandler(RequestHandler):
    """
    Request a session token from Apollo server.
    """

    SUPPORTED_METHODS = ("GET",)

    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json")

        transport = self.application.createTransport()
        logging.info("Acquired session: %s" % transport.token)

        self.write(json.dumps({
            "s" :   transport.token,
            "n":    transport.nonce
        }))

class ActionHandler(RequestHandler):
    """
    Endpoint for sending packets to the Apollo server.
    """

    SUPPORTED_METHODS = ("POST",)

    def post(self, *args, **kwargs):
        token = self.get_argument("s")

        payload = self.get_argument("p")

        try:
            transport = self.application.getTransport(token)
        except KeyError:
            raise HTTPError(500)

        try:
            packet = deserialize_packet(payload)
        except ValueError:
            transport.sendEvent(PacketError(msg="bad packet payload"))
        else:
            packet.dispatch(transport, self.application)

        self.finish()

class EventsHandler(RequestHandler):
    """
    Endpoint for receiving packets from the Apollo server.
    """

    SUPPORTED_METHODS = ("GET",)

    def on_connection_close(self):
        if self.transport:
            self.transport.shutdown()

    def send(self, packet):
        self.finish(packet.dump())

    @asynchronous
    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json")

        token = self.get_argument("s")

        try:
            transport = self.application.getTransport(token)
        except KeyError:
            self.send(PacketError(msg="bad session"))
        else:
            transport.bind(self)
            self.transport = transport

class DylibHandler(RequestHandler):
    """
    Apollo dylib endpoint.
    """

    SUPPORTED_METHODS = ("GET",)

    def get(self, pathspec, *args, **kwargs):
        self.set_header("Content-Type", "text/javascript")
        dylib_data = self.application.dylib_dispatcher.dispatch(pathspec)
        if dylib_data is None:
            raise HTTPError(404)
        self.write(dylib_data)
