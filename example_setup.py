from apollo.server import setup_options
from apollo.server.core import Core

from apollo.server.models import meta
from apollo.server.models.user import User

setup_options()

core = Core()

# very naughty!
meta.session.impl.bind.bind._conn.drop_database(meta.session.impl.bind.database)

user = User()
user.name = "root"
user.password = "test"

user = User()
user.name = "joe"
user.password = "jimmy"

meta.session.save(user)
meta.session.flush_all()

print "Example setup completed."
