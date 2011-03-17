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

import os
from hashlib import sha256

from pymongo.objectid import ObjectId

from apollo.server.component import Component

from apollo.server.models import meta
from apollo.server.models.session import Session

from apollo.server.protocol.packet.packetlogout import PacketLogout

class Transport(Component):
    def __init__(self, core, bound_handler=None):
        super(Transport, self).__init__(core)
        self.bound_handler = bound_handler

        session = Session()
        self.token = session.token
        meta.session.save(session)
        meta.session.flush()

        self.nonce = sha256(os.urandom(64)).hexdigest()
        self.intermedq = []

    def bind(self, bind):
        self.bound_handler = bind
        while self.intermedq:
            self.sendEvent(self.intermedq.pop())

    def sendEvent(self, packet):
        if self.bound_handler is None:
            self.intermedq.append(packet)
            return

        self.bound_handler.send(packet)

        # unbind immediately
        self.bound_handler = None

    def session(self):
        return meta.session.find(Session, { "token" : self.token }).one()

    def shutdown(self):
        self.core.bus.unsubscribeTransport(self)
        self.core.loseTransport(self.token)

        channel = self.core.bus.getChannel("chat.global")
        channel.sendEvent(PacketLogout(username=self.session().get_user()["name"]))

        meta.session.remove(Session, { "token" : self.token })
