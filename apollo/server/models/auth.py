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
import os

import re

from hashlib import sha256
from datetime import datetime

from ming import schema
from ming.orm import MappedClass
from ming.orm import FieldProperty, ForeignIdProperty, RelationProperty

from apollo.server.models import meta
from apollo.server.models.rpg import Profession

from apollo.server.util.compilers import CurveCompiler

class User(MappedClass):
    """
    A user.
    """

    class __mongometa__:
        name = "user"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    """
    The username of the user.
    """

    pwhash = FieldProperty(str)
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
    Convenice property for setting the user's password.
    """

    online = FieldProperty(bool, if_missing=False)
    """
    The status of the user being online.
    """

    registered = FieldProperty(datetime, if_missing=datetime.utcnow)
    """
    Date when user registered.
    """

    sessions = RelationProperty("Session")
    """
    User's sessions.
    """

    group_id = ForeignIdProperty("Group", required=True)
    """
    ID of the group the user belongs to.
    """

    #
    # rpg stuff
    #

    level = FieldProperty(int, if_missing=1)
    """
    User's level.
    """

    profession_id = ForeignIdProperty("Profession", required=True)
    """
    ID of the profession the user belongs to.
    """

    location_id = ForeignIdProperty("Tile", required=True)
    """
    ID of the tile the user is currrently at.
    """

    hp = FieldProperty(int, if_missing=0)
    """
    User's HP.
    """

    @property
    def hpmax(self):
        """
        User's max HP, according to their ``profession.hpcurve``.
        """
        profession = meta.session.get(Profession, self.profession_id)
        return CurveCompiler(profession.hpcurve)(user=self)

    ap = FieldProperty(int, if_missing=0)
    """
    User's AP.
    """

    @property
    def apmax(self):
        """
        User's max AP, according to their ``profession.apcurve``.
        """
        profession = meta.session.get(Profession, self.profession_id)
        return CurveCompiler(profession.apcurve)(user=self)

    xp = FieldProperty(int, if_missing=0)
    """
    User's XP.
    """

    @property
    def xpmax(self):
        """
        User's max XP, according to their ``profession.xpcurve``.
        """
        profession = meta.session.get(Profession, self.profession_id)
        return CurveCompiler(profession.xpcurve)(user=self)

    stats = FieldProperty(schema.Anything)
    """
    User's stats.
    """

    inventory = FieldProperty([schema.ObjectId])
    """
    User's on-hand items.
    """

    def hasPermission(self, permission):
        """
        Check if the user has the specified permission.

        :Parameters:
             * ``permission``
               Permission to check for.
        """
        group = meta.session.get(Group, self.group_id)

        if group is None:
            return False

        for perm in group.permissions:
            if re.match(re.escape(perm).replace("\\*", ".+"), permission):
                return True

        return False

    @staticmethod
    def getUserByName(name):
        """
        Get user by name case-insensitively.

        :Parameters:
             * ``name``
               Username.
        """
        return meta.session.find(User, { "name" : { "$regex" : "^%s$" % re.escape(name.lower()), "$options" : "i" } }).one()

class Session(MappedClass):
    """
    A session that is established when a user makes a connection.
    """

    class __mongometa__:
        name = "session"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    token = FieldProperty(str, if_missing=lambda: sha256(os.urandom(64)).hexdigest())
    """
    Unique session identifier.
    """

    last_active = FieldProperty(datetime, if_missing=datetime.utcnow)
    """
    Last active session time.
    """

    user_id = ForeignIdProperty("User")
    """
    ID of the user connected to this session.
    """

    def getUser(self):
        """
        Get the user connected to this session (if any).
        """
        return meta.session.get(User, self.user_id)

class Group(MappedClass):
    """
    A permission group.
    """
    class __mongometa__:
        name = "group"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    """
    Name of the group, e.g. `Administrator`.
    """

    permissions = FieldProperty([str])
    """
    List of permissions the group has. The wildcard character ``*`` is allowed.
    """

    users = RelationProperty("User")
    """
    Users that are members of this group.
    """