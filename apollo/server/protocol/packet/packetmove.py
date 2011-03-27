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
from apollo.server.models.geography import Chunk, CHUNK_STRIDE, Tile

from apollo.server.util.decorators import requireAuthentication

from apollo.server.util.mathhelper import absolve

from apollo.server.protocol.packet.packetinfo import PacketInfo

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
    def dispatch(self, transport, core):
        user = transport.session().getUser()

        # get the tile the user wants to move to
        ccoords, rcoords = absolve(self.x, self.y, CHUNK_STRIDE)

        # find the chunk
        try:
            chunk = meta.session.find(Chunk, { "location" : { "cx" : ccoords[0], "cy" : ccoords[1] } }).one()
        except ValueError:
            return # XXX: maybe raise an error?

        # find the tile
        try:
            tile = meta.session.find(Tile, { "location" : { "rx" : rcoords[0], "ry" : rcoords[1] }, "chunk_id" : chunk._id }).one()
        except ValueError:
            return # XXX: maybe raise an error?

        user.location_id = tile._id

        meta.session.save(user)
        meta.session.flush_all()

        # inform everyone that the user has moved
        core.bus.broadcast("user.*", PacketMove(
            origin=user.name,
        ))

        # implicitly dispatch a PacketInfo for the calling client
        PacketInfo().dispatch(transport, core)