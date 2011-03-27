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

from ming import schema
from ming.orm import MappedClass
from ming.orm import FieldProperty, ForeignIdProperty, RelationProperty

from apollo.server.models import meta

class Profession(MappedClass):
    """
    An RPG-style profession (think `Warrior`, `Caster`, etc.).
    """

    class __mongometa__:
        name = "profession"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    """
    Name of the profession.
    """

    hpcurve = FieldProperty(str, required=True)
    """
    Python expression that evaluates to the HP for this profession based on user
    stats.

    The variable ``user`` is available for accessing user stats.
    """

    apcurve = FieldProperty(str, required=True)
    """
    Python expression that evaluates to the AP for this profession based on user
    stats.

    The variable ``user`` is available for accessing user stats.
    """

    xpcurve = FieldProperty(str, required=True)
    """
    Python expression that evaluates to the XP for this profession based on user
    stats.

    The variable ``user`` is available for accessing user stats.
    """

    basestats = FieldProperty(schema.Anything)
    """
    Base stats for this profession.
    """

    spawnpoint_id = ForeignIdProperty("Tile")
    """
    ID of the tile that is the profession's default spawnpoint.
    """

class Item(MappedClass):
    """
    An item in a user's inventory.
    """
    class __mongometa__:
        name = "item"
        session = meta.session

    _id = FieldProperty(schema.ObjectId)

    name = FieldProperty(str, required=True)
    """
    Name of the item.
    """

    type
    """
    Item type.
    """

    #
    # python event code
    #
    onuse = FieldProperty(str)
    """
    What should occur when the item is used?
    """
