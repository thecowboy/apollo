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
from sqlalchemy.ext.declarative import declared_attr

from apollo.server.models import meta, PrimaryKeyed, UUIDType
from apollo.server.util.importlib import import_class

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

class RPGUserMixin(object):
    """
    Mixin class for the RPG elements of a user.
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
