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
import uuid

from hashlib import sha256
from datetime import datetime

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import column_property, relationship, aliased, backref
from sqlalchemy.schema import ForeignKey, Column, Index, Table, DDL
from sqlalchemy.types import Integer, Unicode, Boolean, UnicodeText, DateTime

from apollo.server.models import meta, MessagableMixin, PrimaryKeyed, UUIDType, CaseInsensitiveComparator, JSONSerializedType

from apollo.server.util.importlib import import_class

group_security_domains = Table("group_security_domains", meta.Base.metadata,
   Column("group_id", UUIDType, ForeignKey("groups.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
   Column("security_domain_id", UUIDType, ForeignKey("security_domains.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
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

    @declared_attr
    def inventory(cls):
        return relationship("Item", "user_inventory")

    @declared_attr
    def stats(cls):
        return relationship("UserStat")

    hp = Column("hp", Integer, nullable=False, default=0)
    """
    User's HP.
    """

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

    def initializeStats(self):
        sess = meta.Session()
        for base_stat in self.profession.base_stats:
            user_stat = UserStat(user_id=self.id, skill_id=base_stat.skill_id, value=base_stat.value)
            sess.add(user_stat)
        sess.commit()

class Group(meta.Base, PrimaryKeyed, MessagableMixin):
    """
    A permission group.
    """
    __tablename__ = "groups"

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the group, e.g. `Administrator`.
    """

    security_domains = relationship("SecurityDomain", "group_security_domains")
    """
    The security domains belonging to the group.
    """

    users = relationship("User", backref="group")
    """
    The users belonging to the group.
    """

class SecurityDomain(meta.Base, PrimaryKeyed):
    """
    A security domain.
    """
    __tablename__ = "security_domains"

    id = Column("id", UUIDType, primary_key=True, default=uuid.uuid4, nullable=False)
    """
    This is required for the relationship.
    """

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the security domain.
    """

    parent_id = Column("parent_id", UUIDType, ForeignKey("security_domains.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    """
    The parent ID of the security domain.
    """

    parent = relationship("SecurityDomain", backref=backref("children", uselist=True), remote_side=[id], uselist=False)
    """
    The parent of the security domain.
    """

    @classmethod
    def byPath(cls, path):
        """
        Get a security domain by path.

        :Parameters:
          * ``path``
            Path to use, e.g. ``apollo.admin.clobber``.
        """
        query = meta.Session().query(cls)

        path_parts = path.split(".")
        query = query.filter(cls.name == path_parts[-1])

        for part in path_parts[:-1:-1]:
            part_alias = aliased(cls)
            query = query.join((part_alias, cls.parent)).filter(part_alias.name == part)

        return query.one()

class User(meta.Base, PrimaryKeyed, MessagableMixin, RPGUserPartial):
    """
    A user.
    """
    __tablename__ = "users"

    name = column_property(Column("name", Unicode(255), nullable=False), comparator_factory=CaseInsensitiveComparator)
    """
    The username of the user.
    """

    pwhash = Column("pwhash", Unicode(64), nullable=False)
    """
    The password hash of the user (see ``_set_password`` for how this is
    calculated).
    """

    def _set_password(self, value):
        """
        Setter function for the user's password hash.

        :Parameters:
             * ``value``
               Plaintext password to encode.
        """
        self.pwhash = sha256("%s:%s" % (self.name.lower(), value)).hexdigest().decode("utf-8")

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

    def inDomain(self, domain):
        """
        Check if the user is part of a security domain specified.

        :Parameters:
             * ``domain``
               Domain to check.
        """
        sess = meta.Session()

        # TODO: horrible, terrible!
        domains = [domain]

        while domains[-1].parent_id is not None:
            domains.append(sess.query(SecurityDomain).get(domains[-1].parent_id))

        for user_domain in self.group.security_domains:
            query = sess.query(SecurityDomain).filter()

        for perm in self.group.permissions:
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

#try:
#    # use a DDL index because functional ones are not yet available
#    DDL("CREATE UNIQUE INDEX idx_name ON %(fullname)s (lower(name))").execute_at("after-create", User.__table__)
#except ProgrammingError:

# some databases don't support functional indexes (MySQL in particular), so just make a normal one and pray nothing bad happens
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
from apollo.server.models.rpg import UserStat