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

import uuid

from hashlib import sha256
from datetime import datetime

from sqlalchemy.orm import column_property, relationship, aliased, backref
from sqlalchemy.schema import ForeignKey, Column, Index, Table
from sqlalchemy.types import Integer, Unicode, Boolean, DateTime

from apollo.server.models import meta, MessagableMixin, PrimaryKeyed, UUIDType, CaseInsensitiveComparator
from apollo.server.models.rpg import RPGUserMixin

group_security_domains = Table("group_security_domains", meta.Base.metadata,
   Column("group_id", UUIDType, ForeignKey("groups.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
   Column("security_domain_id", UUIDType, ForeignKey("security_domains.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
)

DIRECTLY_IN_DOMAIN = 1
INDIRECTLY_IN_DOMAIN = 2

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

    def inDomain(self, domain):
        if domain in self.security_domains:
            return DIRECTLY_IN_DOMAIN

        # TODO: horrible, terrible! fix this with a PROPER query!
        target_path = domain.getPath() + "."

        domain_paths = []
        for domain in self.security_domains:
            domain_paths.append(domain.getPath() + ".")

        if any(target_path.startswith(path) for path in domain_paths):
            return INDIRECTLY_IN_DOMAIN

        return False

Index("idx_group_name", Group.name, unique=True)

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

    def getPath(self):
        # TODO: somewhat horrible, fix this with a better query
        current_domain = self
        path = [self.name]
        while current_domain.parent is not None:
            current_domain = current_domain.parent
            path.append(current_domain.name)
        return ".".join(path[::-1])

class User(meta.Base, PrimaryKeyed, MessagableMixin, RPGUserMixin):
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
        return self.group.inDomain(domain)

    # a few overrides to avoid sending packets to offline people who can't
    # actually process them
    def sendEx(self, bus, packet):
        if self.online:
            super(User, self).sendEx(bus, packet)

    def sendInter(self, bus, packet):
        if self.online:
            super(User, self).sendInter(bus, packet)

Index("idx_user_name", User.name, unique=True)

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