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

from pymongo.objectid import ObjectId

from hashlib import sha256
from datetime import datetime

from ming import schema
from ming.orm import MappedClass
from ming.orm import FieldProperty, ForeignIdProperty, RelationProperty

from apollo.server.models import meta
from apollo.server.models.group import Group

class User(MappedClass):
    class __mongometa__:
        name = "user"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    pwhash = FieldProperty(str)

    def _set_password(self, value):
        self.pwhash = sha256("%s:%s" % (self.name.lower(), value)).hexdigest()

    password = property(fset=_set_password)

    online = FieldProperty(bool, if_missing=False)

    registered = FieldProperty(datetime, if_missing=datetime.utcnow)

    sessions = RelationProperty("Session")

    group_id = ForeignIdProperty("Group", required=True)

    # rpg stuff
    level = FieldProperty(int, if_missing=1)
    profession_id = ForeignIdProperty("Profession", required=True)
    location_id = ForeignIdProperty("Tile", required=True)

    hp = FieldProperty(int, if_missing=0)
    ap = FieldProperty(int, if_missing=0)
    xp = FieldProperty(int, if_missing=0)

    stats = FieldProperty(schema.Anything)

    def hasPermission(self, permission):
        group = meta.session.get(Group, self.group_id)

        if group is None:
            return False

        for perm in group.permissions:
            if re.match(re.escape(perm).replace("\\*", ".+"), permission):
                return True

        return False

    @staticmethod
    def getUserByName(name):
        return meta.session.find(User, { "name" : { "$regex" : "^%s$" % re.escape(name.lower()), "$options" : "i" } }).one()
