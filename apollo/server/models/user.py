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

from hashlib import sha256
from datetime import datetime

from ming import schema
from ming.orm import MappedClass
from ming.orm import FieldProperty, ForeignIdProperty, RelationProperty

from apollo.server.models import meta

class User(MappedClass):
    class __mongometa__:
        name = "user"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str)
    pwhash = FieldProperty(str)

    def _set_password(self, value):
        self.pwhash = sha256("%s:%s" % (self.name.lower(), value)).hexdigest()

    password = property(fset=_set_password)

    online = FieldProperty(bool, if_missing=False)

    last_active = FieldProperty(datetime, if_missing=datetime.utcnow)
    registered = FieldProperty(datetime, if_missing=datetime.utcnow)

    sessions = RelationProperty("Session")
    group_id = ForeignIdProperty("Group")

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

from apollo.server.models.session import Session
from apollo.server.models.group import Group

MappedClass.compile_all()
