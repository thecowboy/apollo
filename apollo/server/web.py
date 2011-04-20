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

"""
Apollo's HTTP frontend handlers.
"""

from datetime import datetime, timedelta

import json

import logging

from tornado.options import options
from tornado.web import RequestHandler, asynchronous, HTTPError
import uuid

from apollo.server.messaging.consumer import Consumer

from apollo.server.models import meta
from apollo.server.models.auth import Session

from apollo.server.protocol.packet import ORIGIN_EX
from apollo.server.protocol.packet.meta import deserializePacket
from apollo.server.protocol.packet.packeterror import PacketError
from apollo.server.protocol.packet.packetlogout import PacketLogout

class FrontendHandler(RequestHandler):
    """
    Send the user the Apollo client frontend.
    """

    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "text/html; charset=utf8")
        self.write(self.application.loader.load("frontend.html").generate())

class SessionHandler(RequestHandler):
    """
    Request a session token from Apollo server.
    """

    SUPPORTED_METHODS = ("GET",)

    def get(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json")

        session = Session()
        sess = meta.Session()
        sess.add(session)
        sess.commit()

        # declare queue
        self.application.bus.declareQueue(
            "ex-%s" % session.id.hex,
            lambda *args: session.queueBind(self.application.bus, session)
        )

        logging.info("Acquired session: %s" % session.id)

        self.write(json.dumps({
            "s" :   session.id.hex
        }))

class ActionHandler(RequestHandler):
    """
    Endpoint for sending packets to the Apollo server.
    """

    SUPPORTED_METHODS = ("POST",)

    def post(self, *args, **kwargs):
        self.token = uuid.UUID(hex=self.get_argument("s"))
        session = meta.Session().query(Session).get(self.token)

        payload = self.get_argument("p")

        try:
            packet = deserializePacket(payload)
            packet._origin = ORIGIN_EX
        except ValueError:
            self.application.bus.send("ex.session.%s" % session.id, PacketError(msg="bad packet payload"))
        else:
            packet.dispatch(self.application, session)

        self.finish()

class EventsHandler(RequestHandler):
    """
    Endpoint for receiving packets from the Apollo server.
    """

    SUPPORTED_METHODS = ("GET",)

    def on_connection_close(self):
        session = meta.Session().query(Session).get(self.token)

        if session is None:
            return

        user = session.user
        if not user:
            return

        if not self.clean:
            user.sendInter(self.application.bus, PacketLogout(msg="Connection closed"))

    def finish(self, chunk=None):
        super(EventsHandler, self).finish(chunk)
        self.clean = True

    @asynchronous
    def get(self, *args, **kwargs):
        self.clean = False

        self.set_header("Content-Type", "application/json")

        self.token = self.get_argument("s")
        self.consumer = Consumer(self)

        self.consumer.eat()

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
