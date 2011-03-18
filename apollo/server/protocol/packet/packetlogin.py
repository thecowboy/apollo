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

import re
from hashlib import sha256

from apollo.server.protocol.packet import Packet

from apollo.server.models import meta
from apollo.server.models.user import User

from apollo.server.protocol.packet.packetlogout import PacketLogout

class PacketLogin(Packet):
    name = "login"

    def dispatch(self, transport, core):
        user_cursor = meta.session.find(User, { "name" : { "$regex" : "^%s$" % re.escape(self.username.lower()), "$options" : "i" } })

        try:
            user = user_cursor.one()
        except ValueError:
            transport.sendEvent(PacketLogout())
            return

        if self.pwhash != sha256(self.nonce + user.pwhash + transport.nonce).hexdigest():
            transport.sendEvent(PacketLogout())
            return

        session = transport.session()
        session.user_id = user._id
        meta.session.save(session)
        meta.session.flush()

        transport.sendEvent(PacketLogin())

        user_channel = core.bus.getChannel("user.%s" % user._id)
        user_channel.processEvent(PacketLogout())
        user_channel.subscribeTransport(transport)

        global_channel = core.bus.getChannel("global")
        global_channel.subscribeTransport(transport)
        global_channel.sendEvent(PacketLogin(username=transport.session().get_user()["name"]))
