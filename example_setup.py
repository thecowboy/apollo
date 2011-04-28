import json
import sys
import logging
import random

from apollo.server import skeletonSetup

from apollo.server.render.supervisor import RendererSupervisor

from apollo.server.models import meta

from apollo.server.models.auth import User, Group, SecurityDomain
from apollo.server.models.rpg import Profession, ProfessionBaseStat, Skill

from apollo.server.models.geography import Terrain, Realm, Chunk, CHUNK_STRIDE, Tile

# initialize
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    skeletonSetup()

    sess = meta.Session()
    meta.Base.metadata.drop_all(sess.bind)
    print "Creating tables..."
    meta.Base.metadata.create_all(sess.bind)

    # set spawn
    SPAWN_X = 0
    SPAWN_Y = 1

    # create terrain
    print "Generating terrain information..."

    terrains = [
        Terrain(name=u"Grass", img=u"grass"),
        Terrain(name=u"Sand", img=u"sand")
    ]
    sess.add_all(terrains)
    sess.commit()

# create realm
    realm = Realm(
        name=u"Best Realm Ever",
        cw=10,
        ch=10
    )
    sess.add(realm)
    sess.commit()

    # BEST TERRAIN GENERATOR EVER
    print "Generating realm..."

    MAX_TILES = realm.cw * CHUNK_STRIDE * realm.ch * CHUNK_STRIDE

    num_tiles = 0
    for cx in xrange(0, realm.cw):
        for cy in xrange(0, realm.ch):
            chunk = Chunk(
                cx=cx,
                cy=cy,
                realm_id=realm.id
            )
            sess.add(chunk)
            sess.commit()
            for rx in xrange(0, CHUNK_STRIDE):
                for ry in xrange(0, CHUNK_STRIDE):
                    x = cx * CHUNK_STRIDE + rx
                    y = cy * CHUNK_STRIDE + ry

                    tile = Tile(
                        rx=rx,
                        ry=ry,
                        chunk_id=chunk.id,
                        terrain_id=terrains[random.randrange(0, len(terrains))].id
                    )
                    sess.add(tile)
                    num_tiles += 1

                    if not num_tiles % 1000:
                        print "Generated tiles: %d/%d\r" % (num_tiles, MAX_TILES),
                        sys.stdout.flush()

                    if x == SPAWN_X and y == SPAWN_Y:
                        spawntile = tile
            sess.commit()

    print "Generated tiles: %d/%d" % (num_tiles, num_tiles)

    print "Rendering chunks..."

    renderer = RendererSupervisor()
    renderer.go()
    renderer.renderRealm(realm.id)
    renderer.stop()

    print "Chunks rendered."

    print "Populating with first-run data..."

    # create professions
    tester = Profession(
        name=u"Tester",
        assoc_class=u"system.professions.Tester",
        spawnpoint_id=spawntile.id
    )
    sess.add(tester)
    sess.commit()

    # create skills and base stats
    attack_skill = Skill(name=u"Attack")
    sess.add(attack_skill)
    sess.commit()

    tester_base_attack = ProfessionBaseStat(skill_id=attack_skill.id, profession_id=tester.id, value=10)
    sess.add(tester_base_attack)
    sess.commit()

    # setup security domains
    print "Setting up security domains..."
    root_domain = SecurityDomain(name=u"apollo")
    sess.add(root_domain)
    sess.commit()

    server_domain = SecurityDomain(name=u"server", parent_id=root_domain.id)
    sess.add(server_domain)
    sess.commit()

    admin_domain = SecurityDomain(name=u"admin", parent_id=server_domain.id)
    sess.add(admin_domain)
    sess.commit()

    admin_clobber_domain = SecurityDomain(name=u"clobber", parent_id=admin_domain.id)
    sess.add(admin_clobber_domain)
    sess.commit()

    moderator_domain = SecurityDomain(name=u"moderator", parent_id=server_domain.id)
    sess.add(moderator_domain)
    sess.commit()

    moderator_kick_domain = SecurityDomain(name=u"kick", parent_id=moderator_domain.id)
    sess.add(moderator_kick_domain)
    sess.commit()

    # create groups
    players = Group(
        name=u"Players"
    )
    sess.add(players)

    admins = Group(
        name=u"Administrators"
    )
    admins.security_domains.append(root_domain)
    sess.add(admins)
    sess.commit()

    # create users
    user = User(
        name=u"rfw",
        group_id=admins.id,
        profession_id=tester.id,
        location_id=spawntile.id,

        level=10,

        hp=1,
        ap=1,
        xp=1
    )
    user.password = "iscool"
    sess.add(user)
    sess.commit()
    user.initializeStats()
    sess.merge(user)
    sess.commit()

    user = User(
        name=u"rlew",
        group_id=admins.id,
        profession_id=tester.id,
        location_id=spawntile.id,

        hp=1,
        ap=1,
        xp=1
    )
    user.password = "stinx"
    sess.add(user)
    sess.commit()
    user.initializeStats()
    sess.merge(user)
    sess.commit()


    user = User(
        name=u"noshi",
        group_id=players.id,
        profession_id=tester.id,
        location_id=spawntile.id
    )
    user.password = "isgat"
    sess.add(user)
    sess.commit()
    user.initializeStats()
    sess.merge(user)
    sess.commit()

    print "Example setup completed."
