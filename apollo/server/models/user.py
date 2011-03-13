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
        salt = sha256(os.urandom(64)).hexdigest()[:16]
        self.pwhash = sha256(salt + value).hexdigest() + salt

    password = property(fset=_set_password)

    def check_password(self, value):
        salt = self.pwhash[64:]
        return sha256(salt + value).hexdigest() + salt == self.pwhash

    last_active = FieldProperty(datetime, if_missing=datetime.utcnow)
    registered = FieldProperty(datetime, if_missing=datetime.utcnow)

    sessions = RelationProperty("Session")

from apollo.server.models.session import Session

MappedClass.compile_all()
