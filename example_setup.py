from apollo.server import Core, setup_options

from apollo.server.models import meta
from apollo.server.models.user import User

setup_options()

core = Core()

user = User()
user.name = "root"
user.password = "test"

meta.session.save(user)
meta.session.flush_all()

print "Example setup completed."
