import random

from apollo.server import setup_options
from apollo.server.core import Core

from apollo.server.models import meta

from apollo.server.models.user import User
from apollo.server.models.group import Group
from apollo.server.models.profession import Profession

from apollo.server.models.terrain import Terrain
from apollo.server.models.realm import Realm
from apollo.server.models.chunk import Chunk
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
terrains = [
    Terrain(name="Grass", img="grass"),
    Terrain(name="Grass", img="grass")
]

# create realm
REALM_WIDTH = 256
REALM_HEIGHT = 256

realm = Realm(
    name="Best Realm Ever",
    size={
        "width" : REALM_WIDTH,
        "height" : REALM_HEIGHT
    }
)

# create chunks + tiles
CHUNK_SIZE = 8

# BEST TERRAIN GENERATOR EVER
for u in xrange(0, REALM_WIDTH, CHUNK_SIZE):
    for v in xrange(0, REALM_HEIGHT, CHUNK_SIZE):
        chunk = Chunk(
            extents={
                "left"  : u,
                "top"   : v,
                "right" : u + CHUNK_SIZE - 1,
                "bottom": v + CHUNK_SIZE - 1
            },
            realm_id=realm._id
        )
        for x in xrange(u, u + CHUNK_SIZE):
            for y in xrange(v, v + CHUNK_SIZE):
                tile = Tile(
                    location={
                        "x" : x,
                        "y" : y
                    },
                    chunk_id=chunk._id,
                    terrain_id=terrains[random.randrange(0, len(terrains))]._id
                )
                if x == SPAWN_X and y == SPAWN_Y:
                    spawntile = tile

# create permissions
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
    stats={
        "hp" : 1,
        "ap" : 1,
        "xp" : 0
    },
    level=10
)
user.password = "iscool"

user = User(
    name="rlew",
    group_id=admins._id,
    profession_id=tester._id,
    location_id=spawntile._id,
    stats={
        "hp" : 1,
        "ap" : 1,
        "xp" : 0
    }
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
