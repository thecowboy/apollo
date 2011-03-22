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

import os
import logging

import Image

from apollo.server.util.mathhelper import isometricTransform

from apollo.server.models import meta

from apollo.server.models.chunk import Chunk, CHUNK_STRIDE
from apollo.server.models.tile import Tile, TILE_WIDTH, TILE_HEIGHT
from apollo.server.models.terrain import Terrain

STATIC_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "static")
"""
Path to the ``/static`` directory.
"""

STATIC_TILE_PATH = os.path.join(STATIC_PATH, "tiles")
"""
Path to the ``/static/tiles`` directory.
"""

STATIC_CHUNK_PATH = os.path.join(STATIC_PATH, "chunks")
"""
Path to the ``/static/chunks`` directory.
"""

class Renderer(object):
    """
    Facilitates rendering a chunk to an image.
    """

    def renderAll(self, realm_id):
        """
        Render all chunks of a given realm.

        :Parameters:
             * ``realm_id``
               The ID of the realm.
        """
        for chunk in meta.session.find(Chunk, { "realm_id" : realm_id }).sort([ ("location.cx", 1), ("location.cy", 1) ]):
            self.render(chunk._id)

    def render(self, chunk_id):
        """
        Render a given chunk.

        :Parameters:
             * ``chunk_id``
               The ID of the chunk.
        """
        img_cache = {}

        CHUNK_WIDTH = CHUNK_STRIDE * TILE_WIDTH
        CHUNK_HEIGHT = CHUNK_STRIDE * TILE_HEIGHT
        CHUNK_MAXHEIGHT = (CHUNK_STRIDE + 1) * TILE_HEIGHT

        chunk_img = Image.new(
            "RGBA",
            (
                CHUNK_WIDTH,
                CHUNK_MAXHEIGHT
            ),
            (0, 0, 0, 0)
        )

        chunk = meta.session.get(Chunk, chunk_id)
        logging.info("Rendering chunk at (%d, %d)" % (chunk.location.cx, chunk.location.cy))

        for tile in meta.session.find(Tile, { "chunk_id" : chunk._id }).sort([ ("location.rx", 1), ("location.ry", 1) ]):
            terrain = meta.session.get(Terrain, tile.terrain_id)
            tx, ty = isometricTransform(tile.location.rx, tile.location.ry)

            if terrain.img not in img_cache:
                img_cache[terrain.img] = Image.open(os.path.join(STATIC_TILE_PATH, "%s.png" % terrain.img))
            tile_img = img_cache[terrain.img]
            chunk_img.paste(
                tile_img,
                (
                    int(round(tx * TILE_WIDTH + CHUNK_WIDTH / 2 - TILE_WIDTH / 2)),
                    int(round(ty * TILE_HEIGHT))
                ),
                tile_img
            )

        chunk_img.save(os.path.join(STATIC_CHUNK_PATH, "%d.%d.png" % (chunk.location.cx, chunk.location.cy)))
        chunk.fresh = True
        meta.session.save(chunk)
