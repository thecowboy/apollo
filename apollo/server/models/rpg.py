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

from sqlalchemy import Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean, UnicodeText

from apollo.server.models import meta, PrimaryKeyed, UUIDType

user_inventory = Table("user_inventory", meta.Base.metadata,
   Column("user_id", UUIDType, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False),
   Column("item_id", UUIDType, ForeignKey("items.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
)

class Profession(meta.Base, PrimaryKeyed):
    """
    An RPG-style profession (think `Warrior`, `Caster`, etc.).
    """
    __tablename__ = "professions"

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the profession.
    """

    assoc_class = Column("assoc_class", Unicode(255), nullable=False)
    """
    Associated system profession class.
    """

    spawnpoint_id = Column("spawnpoint_id", ForeignKey("tiles.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    ID of the tile that is the profession's default spawnpoint.
    """

    users = relationship("User", backref="profession")

    base_stats = relationship("ProfessionBaseStat")

class UserStat(meta.Base, PrimaryKeyed):
    __tablename__ = "user_stats"

    user_id = Column("user_id", ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    skill_id = Column("skill_id", ForeignKey("skills.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    value = Column("value", Integer, nullable=False)

class ProfessionBaseStat(meta.Base, PrimaryKeyed):
    __tablename__ = "profession_base_stats"

    profession_id = Column("profession_id", ForeignKey("professions.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    skill_id = Column("skill_id", ForeignKey("skills.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    value = Column("value", Integer, nullable=False)

class Skill(meta.Base, PrimaryKeyed):
    """
    A skill, e.g. attack, defense, etc.
    """
    __tablename__ = "skills"

    name = Column("name", Unicode(255), nullable=False)

class ItemType(meta.Base, PrimaryKeyed):
    __tablename__ = "item_types"

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the item type.
    """

    assoc_class = Column("assoc_class", Unicode(255), nullable=False)
    """
    Associated system item class.
    """

    items = relationship("Item", backref="type")

class Item(meta.Base, PrimaryKeyed):
    """
    An item in a user's inventory.
    """
    __tablename__ = "items"

    name = Column("name", Unicode(255), nullable=False)
    """
    Name of the item.
    """

    type_id = Column("type_id", ForeignKey("item_types.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    """
    Item type.
    """

    assoc_params= Column("assoc_params", UnicodeText, nullable=False)
    """
    Parameters for the associated class.
    """

from apollo.server.models.auth import User
from apollo.server.models.geography import Tile
