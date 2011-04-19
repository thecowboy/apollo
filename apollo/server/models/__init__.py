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

"""
Models that represent database items and provide convenience methods.
"""

import uuid

from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.schema import Column
from sqlalchemy.types import String
from sqlalchemy import func

UUIDType = String(32)

class PrimaryKeyed(object):
    id = Column("id", UUIDType, primary_key=True, default=lambda: uuid.uuid4().hex, nullable=False)

class MessagableMixin(object):
    def sendEx(self, bus, packet):
        bus.send("ex.%s.%s" % (self.__class__.__name__.lower(), self._id), packet)

    def sendInter(self, bus, packet):
        bus.send("inter.%s.%s" % (self.__class__.__name__.lower(), self._id), packet)

    def queueBind(self, bus, session, callback=None):
        bus.bindQueue("ex-%s" % session._id, "ex.%s.%s" % (self.__class__.__name__.lower(), self._id), callback)

    def queueUnbind(self, bus, session, callback=None):
        bus.unbindQueue("ex-%s" % session._id, "ex.%s.%s" % (self.__class__.__name__.lower(), self._id), callback)

class CaseInsensitiveComparator(ColumnProperty.Comparator):
    def __eq__(self, other):
        return func.lower(self.__clause_element__()) == func.lower(other)
