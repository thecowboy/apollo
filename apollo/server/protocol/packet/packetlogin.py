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

from hashlib import sha256

from apollo.server.protocol.packet import Packet

from apollo.server.models import meta
from apollo.server.models.auth import User

from apollo.server.protocol.packet.packetlogout import PacketLogout

class PacketLogin(Packet):
    """
    Log into the server, or inform the client a user has logged in.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``username``
           Username of user who has logged in (empty if it is the connected
           client's packet).

         * ``pwhash``
           Password hashed with client and server nonce (client to server only).

         * ``nonce``
           Client nonce (client to server only).
    """
    name = "login"

    def dispatch(self, transport, core):
        try:
            user = User.getUserByName(self.username)
        except ValueError:
            transport.sendEvent(PacketLogout())
            return

        if self.pwhash != sha256(self.nonce + sha256(user.pwhash + transport.nonce).hexdigest()).hexdigest():
            transport.sendEvent(PacketLogout())
            return

        session = transport.session()
        session.user_id = user._id
        meta.session.save(session)
        meta.session.flush()

        transport.sendEvent(PacketLogin())

        # HACK: broadcasting to a cross channel does not work, as it will send
        #       the logout packet after the login packet!
        #
        #       if anyone has a better idea tell me :(
        for connection in core.connections.values():
            if connection.session().user_id == user._id and connection is not transport:
                connection.shutdown("Coexistence not permitted")

        transport.consume()

        core.bus.broadcast("user.*", PacketLogin(username=user.name))
        user.online = True
        meta.session.flush_all()
