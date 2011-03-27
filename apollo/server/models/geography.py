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

from ming import schema
from ming.orm import MappedClass
from ming.orm import FieldProperty, ForeignIdProperty, RelationProperty

from apollo.server.models import meta

CHUNK_STRIDE = 8
"""
Stride of a chunk, i.e. how many tiles it can contain both horizontally and
vertically.
"""

TILE_WIDTH = 64
"""
Width of a single tile.
"""

TILE_HEIGHT = 32
"""
Height of a single tile (top half not counted).
"""

class Terrain(MappedClass):
    """
    Terrain type.
    """

    class __mongometa__:
        name = "terrain"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    """
    Name of the terrain type.
    """

    img = FieldProperty(str, required=True)
    """
    Image of the terrain type.
    """

class Realm(MappedClass):
    """
    The representation of a "world".
    """

    class __mongometa__:
        name = "realm"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    """
    The name of the realm.
    """

    size = FieldProperty({ "cw" : int, "ch" : int }, required=True)
    """
    The size of the realm, in chunk coordinates.
    """

    chunks = RelationProperty("Chunk")
    """
    The chunks contained in this world.
    """

class Chunk(MappedClass):
    """
    A region of the map ``CHUNK_STRIDE`` high and wide. These are rendered for
    the client to display, instead of the client stitching up its own tiles.
    """
    class __mongometa__:
        name = "chunk"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    location = FieldProperty({
        "cx" : int,
        "cy" : int
    }, required=True)
    """
    Location of the chunk, in chunk coordinates.

    Chunk coordinates are calculated with the expressions ``ax // CHUNK_STRIDE``
    and ``ay // CHUNK_STRIDE``, where ``ax`` and ``ay`` are absolute x and y
    coordinates, respectively.
    """

    fresh = FieldProperty(bool, if_missing=False)
    """
    Chunk is "fresh", i.e. no changes to the tiles that reside within it since
    the last render.
    """

    realm_id = ForeignIdProperty("Realm", required=True)
    """
    ID of the realm the chunk belongs to.
    """

class Tile(MappedClass):
    """
    A tile in the world.
    """

    class __mongometa__:
        name = "tile"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    location = FieldProperty({
        "rx" : int,
        "ry" : int
    }, required=True)
    """
    Location of the tile. These are in coordinates relative to the chunk. They
    have the same scale as aboslute coordinates, and can be calculated with the
    expressions ``ax % CHUNK_STRIDE`` and ``ay % CHUNK_STRIDE``.
    """

    chunk_id = ForeignIdProperty("Chunk", required=True)
    """
    ID of the chunk this tile belongs to.
    """

    terrain_id = ForeignIdProperty("Terrain", required=True)
    """
    ID of the terrain type this tile is.
    """
