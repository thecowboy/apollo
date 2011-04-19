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

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from apollo.server.models import meta
from apollo.server.models.auth import User

from apollo.server.protocol.packet import Packet
from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN
from apollo.server.protocol.packet.packetlogout import PacketLogout

from apollo.server.util.auth import requirePermission, requireAuthentication

class PacketKick(Packet):
    """
    Ask the server to kick a client.

    :Direction of Transfer:
        Client to server only.

    :Data Members:
         * ``target``
           User to kick.

         * ``msg``
           Reason for kick.
    """
    name = "kick"

    @requirePermission("moderator.kick")
    @requireAuthentication
    def dispatch(self, core, session):
        user = session.user

        try:
            target = meta.Session().query(User).filter(User.name==self.target).one()
        except (NoResultFound, MultipleResultsFound):
            user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="User does not exist."))
            return

        if not user.online:
            user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="User is not online."))
            return

        self.msg = self.msg or "(no reason given)"

        target.sendInter(core.bus, PacketLogout(msg="Kicked by server: %s" % self.msg))
