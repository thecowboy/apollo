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
from sqlalchemy.orm import relationship

from sqlalchemy.schema import ForeignKey, Column, Index
from sqlalchemy.types import Integer, Unicode, Boolean, UnicodeText

from apollo.server.models import meta, MessagableMixin, PrimaryKeyed, UUIDType

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

class Terrain(meta.Base, PrimaryKeyed):
    """
    Terrain type.
    """
    __tablename__ = "terrains"

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the terrain type.
    """

    img = Column("img", Unicode(255), nullable=False)
    """
    Image of the terrain type.
    """

    tiles = relationship("Tile", backref="terrain")

class Realm(meta.Base, PrimaryKeyed, MessagableMixin):
    """
    The representation of a "world".
    """
    __tablename__ = "realms"

    name = Column("name", Unicode(255), nullable=False)
    """
    The name of the realm.
    """

    cw = Column("cw", Integer, nullable=False)
    """
    The width of the realm, in chunk coordinates.
    """

    ch = Column("ch", Integer, nullable=False)
    """
    The height of the realm, in chunk coordinates.
    """

    chunks = relationship("Chunk", backref="realm")

class Chunk(meta.Base, PrimaryKeyed):
    """
    A region of the map ``CHUNK_STRIDE`` high and wide. These are rendered for
    the client to display, instead of the client stitching up its own tiles.

    Chunk coordinates are calculated with the expressions ``ax // CHUNK_STRIDE``
    and ``ay // CHUNK_STRIDE``, where ``ax`` and ``ay`` are absolute x and y
    coordinates, respectively.
    """
    __tablename__ = "chunks"

    cx = Column("cx", Integer, nullable=False)
    """
    x-coordinate of the chunk.
    """

    cy = Column("cy", Integer, nullable=False)
    """
    y-coordinate of the chunk.
    """

    fresh = Column("fresh", Boolean, nullable=False, default=False)
    """
    Chunk is "fresh", i.e. no changes to the tiles that reside within it since
    the last render.
    """

    realm_id = Column("realm_id", UUIDType, ForeignKey("realms.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    ID of the realm the chunk belongs to.
    """

    tiles = relationship("Tile", backref="chunk")

Index("idx_cx", Chunk.cx)
Index("idx_cy", Chunk.cy)

class Tile(meta.Base, PrimaryKeyed, MessagableMixin):
    """
    A tile in the world.

    These are in coordinates relative to the chunk. They have the same scale as
    aboslute coordinates, and can be calculated with the expressions
    ``ax % CHUNK_STRIDE`` and ``ay % CHUNK_STRIDE``.
    """
    __tablename__ = "tiles"

    rx = Column("rx", Integer, nullable=False)
    """
    Relative x-coordinate of the tile.
    """

    ry = Column("ry", Integer, nullable=False)
    """
    Relative y-coordinate of the tile.
    """

    chunk_id = Column("chunk_id", UUIDType, ForeignKey("chunks.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    ID of the chunk this tile belongs to.
    """

    terrain_id = Column("terrain_id", UUIDType, ForeignKey("terrains.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    ID of the terrain type this tile is.
    """

    users = relationship("User", backref="location")
    professions_spawn = relationship("Profession", backref="spawnpoint")

Index("idx_rx", Tile.rx)
Index("idx_ry", Tile.ry)

class ConstructType(meta.Base, PrimaryKeyed):
    """
    A type of construct (e.g. house, farm, etc.) in the world.
    """
    __tablename__ = "construct_types"

    mask = Column("mask", UnicodeText, nullable=False)
    """
    A list of tile locations the construct takes up. This is used to determine
    collisions and depth-sorting. Assume ``(0, 0)`` is the origin.
    """

    img = Column("img", Unicode(255), nullable=False)
    """
    Image of the construct.
    """

    img_offset_x = Column("img_offset_x", Integer, nullable=False)
    img_offset_y = Column("img_offset_y", Integer, nullable=False)

    assoc_class = Column("assoc_class", Unicode(255), nullable=False)
    """
    Associated system class for the construct type.
    """

class Construct(meta.Base, PrimaryKeyed):
    """
    A construct (e.g. house, farm, etc.) in the world.
    """
    __tablename__ = "constructs"

    type_id = Column("type_id", UUIDType, ForeignKey("construct_types.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    Construct's type.
    """

    location_id = Column("location_id", UUIDType, ForeignKey("tiles.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    Construct's location.
    """

    assoc_params = Column("assoc_params", UnicodeText, nullable=True)
    """
    Parameters for the construct type, as a JSON object.
    """

from apollo.server.models.auth import User
from apollo.server.models.rpg import Profession
