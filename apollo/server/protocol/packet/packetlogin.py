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

from apollo.server.protocol.packet import Packet, ORIGIN_WEB, ORIGIN_CROSS

from apollo.server.models import meta
from apollo.server.models.auth import User
from apollo.server.protocol.packet.packetinfo import PacketInfo

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

    def _dispatch_web(self, transport, core):
        # stage 1 - perform credential checking
        try:
            user = User.getUserByName(self.username)
        except ValueError:
            transport.sendEvent(PacketLogout()) # nope, you don't even exist
            return

        if self.pwhash != sha256(self.nonce + sha256(user.pwhash + transport.nonce).hexdigest()).hexdigest():
            transport.sendEvent(PacketLogout()) # nope, your hash is incorrect
            return

        # set all the sessions and stuff
        session = transport.session()
        session.user_id = user._id
        meta.session.save(session)
        meta.session.flush()

        # logout existing users
        if user.online:
            core.bus.broadcast("cross.%s" % user._id, PacketLogout(msg="Coexistence not permitted"))

            # in case this is a stale client, we can set it forcibly to offline
            user.online = False
            meta.session.flush()

        # kick off stage 2
        transport.consume()
        core.bus.broadcast("cross.%s" % user._id, PacketLogin())

    def _dispatch_cross(self, transport, core):
        # stage 2 - perform authentication
        user = transport.session().getUser()

        transport.sendEvent(PacketLogin())

        core.bus.broadcast("user.*", PacketLogin(username=user.name))

        # cross cast this info packet
        core.bus.broadcast("cross.loc.%s" % user.location_id, PacketInfo())

        user.online = True
        meta.session.flush()

    def dispatch(self, transport, core):
        if self._origin == ORIGIN_WEB:
            self._dispatch_web(transport, core)
        elif self._origin == ORIGIN_CROSS:
            self._dispatch_cross(transport, core)
