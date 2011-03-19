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

from apollo.server.models import meta
from apollo.server.models.user import User

from apollo.server.protocol.packet import Packet
from apollo.server.protocol.packet.packeterror import PacketError

from apollo.server.util.decorators import requireAuthentication

class PacketChat(Packet):
    name = "chat"

    @requireAuthentication
    def dispatch(self, transport, core):
        if not self.msg.strip(): return

        if self.target:
            try:
                user = User.getUserByName(self.target)
            except ValueError:
                transport.sendEvent(PacketError(severity=PacketError.WARN, msg="User does not exist."))
                return

            if not user.online:
                transport.sendEvent(PacketError(severity=PacketError.WARN, msg="User is not online."))
                return

            core.bus.broadcast("user.%s" % user._id, PacketChat(
                origin=transport.session().getUser().name,
                target=self.target,
                msg=self.msg
            ))

            transport.sendEvent(PacketChat(
                origin=transport.session().getUser().name,
                target=self.target,
                msg=self.msg
            ))
            return

        core.bus.broadcast("user.*", PacketChat(
            origin=transport.session().getUser().name,
            msg=self.msg
        ))
