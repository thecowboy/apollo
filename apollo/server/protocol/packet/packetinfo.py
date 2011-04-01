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

from apollo.server.protocol.packet import Packet

from apollo.server.models import meta
from apollo.server.models.geography import Tile, Chunk, CHUNK_STRIDE, Terrain, Realm
from apollo.server.models.auth import User

from apollo.server.util.decorators import requireAuthentication
from apollo.server.util.mathhelper import dissolve

class PacketInfo(Packet):
    """
    Request information about the current tile from the server, or send the
    client information about the current tile.

    :Direction of Transfer:
        Bidirectional.

    :Data Members:
         * ``location``
           Location of the tile (x, y and realm name).

         * ``terrain``
           Information about the tile's terrain.

         * ``size``
           Realm size.

         * ``things``
           Things present at the tile.
    """

    name = "info"

    @requireAuthentication
    def dispatch(self, core, session):
        user = session.getUser()

        tile = meta.session.get(Tile, user.location_id)

        terrain = meta.session.get(Terrain, tile.terrain_id)
        chunk = meta.session.get(Chunk, tile.chunk_id)

        realm = meta.session.get(Realm, chunk.realm_id)

        # get the players here
        things = []

        users_raw = meta.session.find(User, {
            "location_id" : tile._id,
            "online" : True
        })

        for user_raw in users_raw:
            if user._id == user_raw._id: continue
            things.append({
                "name"  : user_raw.name,
                "level" : user_raw.level,
                "type"  : "user"
            })

        acoords = dissolve(chunk.location.cx, chunk.location.cy, tile.location.rx, tile.location.ry, CHUNK_STRIDE)

        core.bus.broadcast("ex.user.%s" % user._id, PacketInfo(
            location={
                "x"     : acoords[0],
                "y"     : acoords[1],
                "realm" : realm.name,
            },
            terrain={
                "img"   : terrain.img,
                "name"  : terrain.name,
            },
            size={
                "cw"    : realm.size.cw,
                "ch"    : realm.size.ch
            },
            things=things
        ))
