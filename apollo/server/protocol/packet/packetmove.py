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
from sqlalchemy.sql.expression import and_

from apollo.server.protocol.packet import Packet

from apollo.server.models import meta
from apollo.server.models.geography import Chunk, CHUNK_STRIDE, Tile

from apollo.server.util.auth import requireAuthentication

from apollo.server.util.mathhelper import absolve

from apollo.server.protocol.packet.packeterror import PacketError, SEVERITY_WARN
from apollo.server.protocol.packet.packetinfo import PacketInfo

from apollo.system import PredicateNotMatchedError

class PacketMove(Packet):
    """
    Request the server to move the client, or inform a client that another
    client has moved.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``x``
           x-coordinate to move to.

         * ``y``
           y-coordinate to move to.
    """

    name = "move"

    @requireAuthentication
    def dispatch(self, core, session):
        user = session.user
        sess = meta.Session()

        old_tile = sess.query(Tile).get(user.location_id)

        # get the tile the user wants to move to
        ccoords, rcoords = absolve(self.x, self.y, CHUNK_STRIDE)

        # find the chunk
        try:
            chunk = sess.query(Chunk).filter(and_(Chunk.cx == ccoords[0], Chunk.cy == ccoords[1])).one()
        except (NoResultFound, MultipleResultsFound):
            user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="Cannot move there."))
            return False

        # find the tile
        try:
            tile = sess.query(Tile).filter(and_(Tile.rx == rcoords[0], Tile.ry == rcoords[1], Tile.chunk_id == chunk.id)).one()
        except (NoResultFound, MultipleResultsFound):
            user.sendEx(core.bus, PacketError(severity=SEVERITY_WARN, msg="Cannot move there."))
            return False

        user.location_id = tile.id

        sess.merge(user)
        sess.commit()

        # rebind queue to new position
        old_tile.queueUnbind(core.bus, session)
        tile.queueBind(core.bus, session)

        # some users may require additional info (including this one!)
        tile.sendInter(core.bus, PacketInfo())
        old_tile.sendInter(core.bus, PacketInfo())

        # return true for hooks
        return True
