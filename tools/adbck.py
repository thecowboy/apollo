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
The Apollo database consistency checker.
"""

import sys
import os

dist_root = os.path.join(os.path.dirname(__file__), "..")

# add the apollo path to the pythonpath
sys.path.insert(1, dist_root)

from apollo.server import skeletonSetup
from apollo.server.models import meta
from apollo.server.models.geography import Realm, Chunk, Tile, CHUNK_STRIDE

if __name__ == "__main__":
    skeletonSetup(os.path.join(dist_root, "apollod.conf"))

    print "Apollo Database Consistency Checker\n"

    sess = meta.Session()

    for realm in sess.query(Realm):
        print "Performing consistency check on realm: %s" % realm.id

        ccoords = set()
        tcoords = set()

        for chunk in sess.query(Chunk).filter(Chunk.realm_id == realm.id):
            if chunk.cx < 0 or chunk.cx >= realm.cw:
                print "ERROR: chunk %s has an incorrect cx position! Expected something in the range [0,%d], got %d" % (chunk.id, realm.cw - 1, chunk.cx)
                continue

            if chunk.cy < 0 or chunk.cy >= realm.ch:
                print "ERROR: chunk %s has an incorrect cy position! Expected something in the range [0,%d], got %d" % (chunk.id, realm.ch - 1, chunk.cy)
                continue

            ccoord = (chunk.cx, chunk.cy)
            if ccoord in ccoords:
                print "ERROR: chunk %s does not have a unique position! (%d, %d) is not unique!" % ((chunk.id,) + ccoord)
                continue

            ccoords.add(ccoord)

            for tile in sess.query(Tile).filter(Tile.chunk_id == chunk.id):
                if tile.rx < 0 or tile.ry >= CHUNK_STRIDE:
                    print "ERROR: tile %s has an incorrect rx position! Expected something in the range [0,%d], got %d" % (chunk.id, CHUNK_STRIDE - 1, tile.rx)
                    continue

                if tile.ry < 0 or tile.ry >= CHUNK_STRIDE:
                    print "ERROR: tile %s has an incorrect ry position! Expected something in the range [0,%d], got %d" % (chunk.id, CHUNK_STRIDE - 1, tile.ry)
                    continue

                tcoord = (chunk.cx * CHUNK_STRIDE + tile.rx, chunk.cy * CHUNK_STRIDE + tile.ry)
                if tcoord in tcoords:
                    print "ERROR: tile %s does not have a unique position! (%d, %d) is not unique!" % ((tile.id,) + tcoord)
                    continue

                tcoords.add(tcoord)

        expected_chunks = realm.cw * realm.ch
        actual_chunks = len(ccoords)

        print "Number of chunks: expected %d, got %d - %s" % (expected_chunks, actual_chunks, expected_chunks == actual_chunks and "OK" or "FAIL")

        expected_tiles = expected_chunks * CHUNK_STRIDE * CHUNK_STRIDE
        actual_tiles = len(tcoords)
        print "Number of tiles: expected less than or equal to %d, got %d - %s" % (expected_tiles, actual_tiles, actual_tiles <= expected_tiles and "OK" or "FAIL")

        print ""
