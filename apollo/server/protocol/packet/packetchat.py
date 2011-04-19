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
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from apollo.server.models import meta
from apollo.server.models.auth import User

from apollo.server.protocol.packet import Packet
from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN

from apollo.server.util.auth import requireAuthentication

class PacketChat(Packet):
    """
    Send the client a chat message, or ask the server to relay a chat message.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``target``
           Target of message if from client; origin of message if from server.

         * ``msg``
           Message body.
    """
    name = "chat"

    @requireAuthentication
    def dispatch(self, core, session):
        if not self.msg.strip(): return

        user = session.user

        if self.target:
            try:
                target = meta.Session().query(User).filter(User.name==self.target).one()
            except (NoResultFound, MultipleResultsFound):
                target.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="User does not exist."))
                return

            if not target.online:
                target.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="User is not online."))
                return

            # send packet to target
            target.sendEx(core.bus, PacketChat(
                origin=user.name,
                target=self.target,
                msg=self.msg
            ))

            # send packet to origin
            user.sendEx(core.bus, PacketChat(
                origin=user.name,
                target=self.target,
                msg=self.msg
            ))
            return

        core.bus.broadcastEx(PacketChat(
            origin=user.name,
            msg=self.msg
        ))
