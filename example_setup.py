import sys
import logging

import random
import math

from tornado.options import parse_command_line, parse_config_file

from apollo.server import setupOptions, setupDBSession
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
logging.basicConfig(level=logging.INFO)

setupOptions()
parse_config_file("apollod.conf")
parse_command_line()
setupDBSession()

# clear out the old database (while breaking many, many layers of encapsulation)
meta.session.get(User, "") # connect to the database
meta.session.impl.bind.bind._conn.drop_database(meta.session.impl.bind.database)

# set spawn
SPAWN_X = 10
SPAWN_Y = 23

# create terrain
print "Generating terrain information..."

terrains = [
    Terrain(name="Grass", img="grass"),
    Terrain(name="Rocks", img="rocks")
]

# create realm
realm = Realm(
    name="Best Realm Ever",
    size={
        "cw" : 8,
        "ch" : 8
    }
)

meta.session.flush_all()

# BEST TERRAIN GENERATOR EVER
print "Generating realm..."

MAX_TILES = realm.size.cw * CHUNK_STRIDE * realm.size.ch * CHUNK_STRIDE 

num_tiles = 0
for cx in xrange(0, realm.size.cw):
    for cy in xrange(0, realm.size.ch):
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

                tile = Tile(
                    location={
                        "rx" : rx,
                        "ry" : ry
                    },
                    chunk_id=chunk._id,
                    terrain_id=(terrains[1] if x == SPAWN_X and y == SPAWN_Y else terrains[0])._id
                )
                num_tiles += 1

                if not num_tiles % 1000:
                    print "Generated tiles: %d/%d\r" % (num_tiles, MAX_TILES),
                    sys.stdout.flush()

                if x == SPAWN_X and y == SPAWN_Y:
                    spawntile = tile

print "Generated tiles: %d/%d, flushing..." % (num_tiles, num_tiles)
meta.session.flush_all()

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
