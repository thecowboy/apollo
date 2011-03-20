from apollo.server import setup_options
from apollo.server.core import Core

from apollo.server.models import meta
from apollo.server.models.user import User
from apollo.server.models.group import Group
from apollo.server.models.profession import Profession

setup_options()

core = Core()

# very naughty!
meta.session.impl.bind.bind._conn.drop_database(meta.session.impl.bind.database)

tester = Profession()
tester.name = "Tester"
tester.hpcurve = "10 + user.level * 10"
tester.apcurve = "10 + user.level * 10"
tester.xpcurve = "10 + user.level * 10"

admins = Group()
admins.name = "Administrators"
admins.permissions = [ "*" ]

user = User()
user.name = "rfw"
user.password = "iscool"
user.group_id = admins._id
user.profession_id = tester._id
user.level = 10
user.stats = {
    "hp" : 1,
    "ap" : 1,
    "xp" : 0
}

user = User()
user.name = "ken"
user.password = "blah"
user.stats = {
    "hp" : 1,
    "ap" : 1,
    "xp" : 0
}
user = User()
user.name = "noshi"
user.password = "isgat"

user = User()
user.name = "rlew"
user.password = "stinx"

meta.session.flush_all()

print "Example setup completed."
