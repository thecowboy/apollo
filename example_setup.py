import sys

import random
import math

from apollo.server import setup_options
from apollo.server.core import Core

from apollo.server.render.renderer import Renderer

from apollo.server.models import meta

from apollo.server.models.user import User
from apollo.server.models.group import Group
from apollo.server.models.profession import Profession

from apollo.server.models.terrain import Terrain
from apollo.server.models.realm import Realm
from apollo.server.models.chunk import Chunk, CHUNK_STRIDE
from apollo.server.models.tile import Tile

# initialize
setup_options()

core = Core()


# clear out the old database (while breaking many, many layers of encapsulation)
meta.session.impl.bind.bind._conn.drop_database(meta.session.impl.bind.database)

# set spawn
SPAWN_X = 10
SPAWN_Y = 12

# create terrain
print "Generating terrain information..."

terrains = [
    Terrain(name="Grass", img="grass"),
    Terrain(name="Rocks", img="rocks")
]

# create realm
REALM_WIDTH = 64
REALM_HEIGHT = 64

realm = Realm(
    name="Best Realm Ever",
    size={
        "width" : REALM_WIDTH,
        "height" : REALM_HEIGHT
    }
)

meta.session.flush_all()

# BEST TERRAIN GENERATOR EVER
print "Generating realm..."

MAX_TILES = REALM_WIDTH * REALM_HEIGHT

num_tiles = 0
for cx in xrange(0, int(math.ceil(REALM_WIDTH / float(CHUNK_STRIDE)))):
    for cy in xrange(0, int(math.ceil(REALM_HEIGHT / float(CHUNK_STRIDE)))):
        chunk = Chunk(
            location={
                "cx" : cx,
                "cy" : cy
            },
            realm_id=realm._id
        )
        for rx in xrange(0, CHUNK_STRIDE):
            for ry in xrange(0, CHUNK_STRIDE):
                x = cx * CHUNK_STRIDE + rx
                y = cy * CHUNK_STRIDE + ry

                if x > REALM_WIDTH - 1 or y > REALM_HEIGHT - 1:
                    continue

                tile = Tile(
                    location={
                        "rx" : rx,
                        "ry" : ry
                    },
                    chunk_id=chunk._id,
                    terrain_id=terrains[random.randrange(0, len(terrains))]._id
                )
                num_tiles += 1

                if not num_tiles % 1000:
                    meta.session.flush_all()
                    print "Generated tiles: %d/%d\r" % (num_tiles, MAX_TILES),
                    sys.stdout.flush()

                if x == SPAWN_X and y == SPAWN_Y:
                    spawntile = tile

print "Generated tiles: %d/%d" % (num_tiles, num_tiles)

print "Rendering chunks..."

renderer = Renderer()
renderer.renderAll(realm._id)

print "Chunks rendered."

print "Populating with first-run data..."

# create professions
tester = Profession(
    name="Tester",
    hpcurve="10 + user.level * 10",
    apcurve="10 + user.level * 10",
    xpcurve="10 + user.level * 10",
    spawnpoint_id=spawntile._id
)

# create groups
players = Group(
    name="Players",
    permissions=[]
)

admins = Group(
    name="Administrators",
    permissions=[ "*" ]
)

# create users
user = User(
    name="rfw",
    group_id=admins._id,
    profession_id=tester._id,
    location_id=spawntile._id,

    level=10,

    hp=1,
    ap=1,
    xp=1
)
user.password = "iscool"

user = User(
    name="rlew",
    group_id=admins._id,
    profession_id=tester._id,
    location_id=spawntile._id,

    hp=1,
    ap=1,
    xp=1
)
user.password = "stinx"

user = User(
    name="noshi",
    group_id=players._id,
    profession_id=tester._id,
    location_id=spawntile._id
)
user.password = "isgat"

# we're done!
meta.session.flush_all()

print "Example setup completed."
