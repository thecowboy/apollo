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

from apollo.server.models.auth import User
from apollo.server.models.geography import Tile, Chunk, CHUNK_STRIDE, Realm

from apollo.server.protocol.packet import Packet
from apollo.server.protocol.packet.packeterror import PacketError, WARN

from apollo.server.models import meta
from apollo.server.models.rpg import Profession

from apollo.server.util.decorators import requireAuthentication
from apollo.server.util.compilers import CurveCompiler
from apollo.server.util.mathhelper import dissolve

class PacketUser(Packet):
    """
    Request basic information about either an arbitrary user from the server or
    the current user, or send the client user information.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``target``
           User to request information about. Empty if requesting information
           about current user.

         * ``name``
           User's name. In most cases will be the same value as ``target``.

         * ``level``
           Level of the user.

         * ``profession``
           Name of the user's profession.

         * ``hp``
           User's HP and max HP.

         * ``ap``
           User's AP and max AP.

         * ``xp``
           User's XP and max XP.
    """

    name = "user"

    @requireAuthentication
    def dispatch(self, transport, core):
        if self.target is None:
            user = transport.session().getUser()
        else:
            try:
                user = meta.session.find(User, { "name" : self.target }).one()
            except ValueError:
                transport.sendEvent(PacketError(severity=WARN, msg="User not found."))
                return

        if not user.online:
            # lie about it and pretend the user doesn't exist
            transport.sendEvent(PacketError(severity=WARN, msg="User not found."))
            return

        profession = meta.session.get(Profession, user.profession_id)

        tile = meta.session.get(Tile, user.location_id)
        chunk = meta.session.get(Chunk, tile.chunk_id)

        realm = meta.session.get(Realm, chunk.realm_id)

        acoords = dissolve(chunk.location.cx, chunk.location.cy, tile.location.rx, tile.location.ry, CHUNK_STRIDE)

        packet = PacketUser(
            name=user.name,
            level=user.level,
            profession=profession.name,
            location={
                "x"     : acoords[0],
                "y"     : acoords[1],
                "realm" : realm.name
            },
            hp={ "now" : user.hp, "max" : CurveCompiler(profession.hpcurve)(user=user) },
            ap={ "now" : user.ap, "max" : CurveCompiler(profession.apcurve)(user=user) },
            xp={ "now" : user.xp, "max" : CurveCompiler(profession.xpcurve)(user=user) }
        )

        if self.target is not None:
            packet.target = user.name

        transport.sendEvent(packet)
