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

import re
import json

from hashlib import sha256
from datetime import datetime
from sqlalchemy.exc import ProgrammingError

from tornado.options import options

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.schema import ForeignKey, Column, Index, Table, DDL
from sqlalchemy.types import Integer, Unicode, Boolean, UnicodeText, DateTime, String

from apollo.server.models import meta, MessagableMixin, PrimaryKeyed, UUIDType, CaseInsensitiveComparator

from apollo.server.util.importlib import import_class

user_inventory = Table("user_inventory", meta.Base.metadata,
   Column("user_id", UUIDType, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
   Column("item_id", UUIDType, ForeignKey("items.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
)

class RPGUserPartial(object):
    """
    Partial class for the RPG elements of a user.
    """
    level = Column("level", Integer, nullable=False, default=1)
    """
    User's level.
    """

    @declared_attr
    def profession_id(cls):
        """
        ID of the profession the user belongs to.
        """
        return Column("profession_id", UUIDType, ForeignKey("professions.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    @declared_attr
    def location_id(cls):
        """
        ID of the tile the user is currrently at.
        """
        return Column("location_id", UUIDType, ForeignKey("tiles.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)

    hp = Column("hp", Integer, nullable=False, default=0)
    """
    User's HP.
    """

    @declared_attr
    def inventory(cls):
        return relationship("Item", user_inventory)

    @property
    def hpmax(self):
        """
        User's max HP, according to their ``profession.hpcurve``.
        """
        return import_class(self.profession.assoc_class)(self).hpCurve()

    ap = Column("ap", Integer, nullable=False, default=0)
    """
    User's AP.
    """

    @property
    def apmax(self):
        """
        User's max AP, according to their ``profession.apcurve``.
        """
        return import_class(self.profession.assoc_class)(self).apCurve()

    xp = Column("xp", Integer, nullable=False, default=0)
    """
    User's XP.
    """

    @property
    def xpmax(self):
        """
        User's max XP, according to their ``profession.xpcurve``.
        """
        return import_class(self.profession.assoc_class)(self).xpCurve()


class Group(meta.Base, PrimaryKeyed, MessagableMixin):
    """
    A permission group.
    """
    __tablename__ = "groups"

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the group, e.g. `Administrator`.
    """

    permissions = Column("permissions", UnicodeText, nullable=False)
    """
    List of permissions the group has. The wildcard character ``*`` is allowed.
    """

    users = relationship("User", backref="group")

class User(meta.Base, PrimaryKeyed, MessagableMixin, RPGUserPartial):
    """
    A user.
    """
    __tablename__ = "users"

    name = column_property(Column("name", Unicode(255), nullable=False), comparator_factory=CaseInsensitiveComparator)
    """
    The username of the user.
    """

    pwhash = Column("pwhash", String(64), nullable=False)
    """
    The password hash of the user (see ``_set_password`` for how this is
    calculated).
    """

    def _set_password(self, value):
        """
        Setter function for the user's password hash.

        :Paramater:
             * ``value``
               Plaintext password to encode.
        """
        self.pwhash = sha256("%s:%s" % (self.name.lower(), value)).hexdigest()

    password = property(fset=_set_password)
    """
    Convenience property for setting the user's password.
    """

    online = Column("online", Boolean, nullable=False, default=False)
    """
    The status of the user being online.
    """

    registered = Column("registered", DateTime, nullable=False, default=datetime.utcnow)
    """
    Date when user registered.
    """

    group_id = Column("group_id", UUIDType, ForeignKey("groups.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    ID of the group the user belongs to.
    """

    sessions = relationship("Session", backref="user")

    def hasPermission(self, permission):
        """
        Check if the user has the specified permission.

        :Parameters:
             * ``permission``
               Permission to check for.
        """
        for perm in json.loads(self.group.permissions):
            if re.match(re.escape(perm).replace("\\*", ".+"), permission):
                return True

        return False

    # a few overrides to avoid sending packets to offline people who can't
    # actually process them
    def sendEx(self, bus, packet):
        if self.online:
            super(User, self).sendEx(bus, packet)

    def sendInter(self, bus, packet):
        if self.online:
            super(User, self).sendInter(bus, packet)

try:
    # use a DDL index because functional ones are not yet available
    DDL("CREATE UNIQUE INDEX idx_name ON %(fullname)s (lower(name))").execute_at("after-create", User.__table__)
except ProgrammingError:
    # some databases don't support functional indexes, so just make a normal one and pray nothing bad happens
    Index("idx_name", User.name)

class Session(meta.Base, PrimaryKeyed, MessagableMixin):
    """
    A session that is established when a user makes a connection.
    """
    __tablename__ = "sessions"

    last_active = Column("last_active", DateTime, nullable=False, default=datetime.utcnow)
    """
    Last active session time.
    """

    user_id = Column("user_id", UUIDType, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    """
    ID of the user connected to this session.
    """

from apollo.server.models.geography import Tile
