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
from apollo.server.models.auth import Session
from apollo.server.models.geography import Tile

from apollo.server.protocol.packet import Packet, ORIGIN_INTER

from apollo.server.util.auth import requireAuthentication

from apollo.server.models import meta

from apollo.server.protocol.packet.packetinfo import PacketInfo

class PacketLogout(Packet):
    """
    Log out of the server, or inform the client a user has logged out.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``username``
           Username of user who has logged out (empty if it is the connected
           client's packet).
    """
    name = "logout"

    @requireAuthentication
    def dispatch(self, core, session):
        if self._origin == ORIGIN_INTER:
            msg = self.msg or "Reason unknown"
        else:
            msg = "User logout: " + (self.msg or "(no reason given)")

        sess = meta.Session()

        user = session.user

        if user is not None:
            # tell user logout was successful
            user.sendEx(core.bus, PacketLogout(msg=msg))

            # send the logout
            core.bus.broadcastEx(PacketLogout(username=user.name, msg=msg))

            # unset online
            user.online = False

            # send packetinfo to relevant people
            tile = sess.query(Tile).get(user.location_id)
            tile.sendInter(core.bus, PacketInfo())

            # delete all sessions and queues associated
            for session in user.sessions:
                core.bus.deleteQueue("ex-%s" % session.id)

            sess.query(Session).filter(Session.user_id == user.id).delete()

            sess.commit()
