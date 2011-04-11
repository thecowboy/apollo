import sys
import logging
import random

from apollo.server import skeletonSetup

from apollo.server.render.supervisor import RendererSupervisor

from apollo.server.models import meta

from apollo.server.models.auth import User, Group
from apollo.server.models.rpg import Profession

from apollo.server.models.geography import Terrain, Realm, Chunk, CHUNK_STRIDE, Tile

# initialize
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    skeletonSetup()

    # clear out the old database (while breaking many, many layers of encapsulation)
    meta.session.get(User, "") # connect to the database
    conn = meta.session.impl.bind.bind._conn
    conn.drop_database(meta.session.impl.bind.database)
    db = conn[meta.session.impl.bind.database]

    # set spawn
    SPAWN_X = 0
    SPAWN_Y = 1

    # create terrain
    print "Generating terrain information..."

    terrains = [
        Terrain(name="Grass", img="grass"),
        Terrain(name="Sand", img="sand")
    ]

    # create realm
    realm = Realm(
        name="Best Realm Ever",
        size={
            "cw" : 10,
            "ch" : 10
        }
    )

    meta.session.flush_all()

    # BEST TERRAIN GENERATOR EVER
    print "Generating realm..."

    MAX_TILES = realm.size.cw * CHUNK_STRIDE * realm.size.ch * CHUNK_STRIDE

    db.chunk.create_index([ ("location.cx", 1), ("location.cy", 1) ], unique=True)
    db.tile.create_index([ ("location.rx", 1), ("location.ry", 1) ])

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
                        terrain_id=terrains[random.randrange(0, len(terrains))]._id
                    )
                    num_tiles += 1

                    if not num_tiles % 1000:
                        print "Generated tiles: %d/%d\r" % (num_tiles, MAX_TILES),
                        sys.stdout.flush()

                    if x == SPAWN_X and y == SPAWN_Y:
                        spawntile = tile

    print "Generated tiles: %d/%d, flushing to database..." % (num_tiles, num_tiles)
    meta.session.flush_all()

    print "Rendering chunks..."

    renderer = RendererSupervisor()
    renderer.go()
    renderer.renderRealm(realm._id)
    renderer.stop()

    print "Chunks rendered."

    print "Populating with first-run data..."

    # create professions
    tester = Profession(
        name="Tester",
        assoc_class="system.professions.Tester",
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
    db.user.create_index([ ("name", 1) ], unique=True)

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

