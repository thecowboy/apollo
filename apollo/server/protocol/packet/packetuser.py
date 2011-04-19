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

from apollo.server.models.auth import User
from apollo.server.models.geography import Tile, Chunk, CHUNK_STRIDE, Realm

from apollo.server.protocol.packet import Packet
from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN

from apollo.server.models import meta
from apollo.server.models.rpg import Profession

from apollo.server.util.auth import requireAuthentication
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
    def dispatch(self, core, session):
        user = session.user
        sess = meta.Session()

        if self.target is None:
            target = user
        else:
            try:
                target = sess.query(User).filter(User.name == self.target).one()
            except (NoResultFound, MultipleResultsFound):
                user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="User not found."))
                return

        if not target.online:
            # lie about it and pretend the user doesn't exist
            user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="User not found."))
            return

        tile = target.location
        chunk = tile.chunk

        acoords = dissolve(chunk.cx, chunk.cy, tile.rx, tile.ry, CHUNK_STRIDE)

        packet = PacketUser(
            name=target.name,
            level=target.level,
            profession=target.profession.name,
            location={
                "x"     : acoords[0],
                "y"     : acoords[1],
                "realm" : chunk.realm.name
            },
            hp={ "now" : target.hp, "max" : target.hpmax },
            ap={ "now" : target.ap, "max" : target.apmax },
            xp={ "now" : target.xp, "max" : target.xpmax }
        )

        if self.target is not None:
            packet.target = target.name

        user.sendEx(core.bus, packet)
