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

"""
Supervisor for the renderer processes.
"""

import os
import logging

import Image

from tornado.options import options

from multiprocessing import Pool

from apollo.server import skeletonSetup
from apollo.server.util.mathhelper import isometricTransform
from apollo.server.models import meta
from apollo.server.models.geography import Chunk, CHUNK_STRIDE, Tile, TILE_WIDTH, TILE_HEIGHT, Terrain

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

def render(chunk_id):
    """
    Render a given chunk.

    :Parameters:
         * ``chunk_id``
           The ID of the chunk.
    """
    try:
        sess = meta.Session()

        img_cache = {}

        CHUNK_WIDTH = CHUNK_STRIDE * TILE_WIDTH
        CHUNK_HEIGHT = CHUNK_STRIDE * TILE_HEIGHT

        chunk_img = Image.new(
            "RGBA",
            (
                CHUNK_WIDTH,
                CHUNK_HEIGHT
            ),
            (0, 0, 0, 0)
        )

        chunk = sess.query(Chunk).get(chunk_id)

        for tile in sess.query(Tile).filter(Tile.chunk_id==chunk.id):
            terrain = sess.query(Terrain).get(tile.terrain_id)
            tx, ty = isometricTransform(tile.rx, tile.ry)

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

        chunk_img.save(os.path.join(STATIC_CHUNK_PATH, "%d.%d.png" % (chunk.cx, chunk.cy)))
        chunk.fresh = True

        sess.add(chunk)
        sess.commit()

        logging.info("Rendered chunk at (%d, %d)" % (chunk.cx, chunk.cy))
    except Exception, e:
        logging.error("Got exception: %s: %s" % (e.__class__.__name__, e))

class RendererSupervisor(object):
    def go(self):
        self.pool = Pool(
            processes=options.render_process_num,
            initializer=skeletonSetup
        )
        logging.info("Started renderer with %d processes" % options.render_process_num)

    def stop(self, safe=True):
        if safe:
            self.pool.close()
        else:
            self.pool.terminate()
        self.pool.join()

    def renderRealm(self, realm_id, callback=None):
        callback = callback or (lambda *args, **kwargs: None)

        chunk_cur = meta.Session().query(Chunk).filter(Chunk.realm_id == realm_id)
        chunk_num = [ 0, chunk_cur.count() ]

        def _callback(*args, **kwargs):
            chunk_num[0] += 1
            if chunk_num[0] == chunk_num[1]:
                callback(*args, **kwargs)

        for chunk in chunk_cur:
            self.renderChunk(chunk.id, callback=_callback)

    def renderChunk(self, chunk_id, callback=None):
        callback = callback or (lambda *args, **kwargs: None)
        self.pool.apply_async(render, (chunk_id,), callback=callback)
