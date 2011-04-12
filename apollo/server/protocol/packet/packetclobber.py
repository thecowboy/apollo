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
from apollo.server.models.geography import Chunk

from apollo.server.protocol.packet import Packet
from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN

from apollo.server.util.auth import requireAuthentication, requirePermission

class PacketClobber(Packet):
    """
    Request that the client clobbers a chunk and reloads it, or request that
    the server rerender a chunk.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``cx``
           Chunk x coordinate.

         * ``cy``
           Chunk y coordinate.
    """
    name = "clobber"

    @requirePermission("admin.clobber")
    @requireAuthentication
    def dispatch(self, core, session):
        user = session.getUser()

        try:
            chunk = meta.session.find(Chunk, { "location" : { "cx" : int(self.cx), "cy" : int(self.cy) } }).one()
        except ValueError:
            core.bus.broadcast("ex.user.%s" % user._id, PacketError(severity=SEVERITY_WARN, msg="Could not find chunk to clobber."))
            return

        core.rendervisor.renderChunk(chunk._id)

        core.bus.broadcast("ex.user.global", PacketClobber(
            cx=self.cx,
            cy=self.cy
        ))
