from sqlalchemy import MetaData, Column, Unicode, Float, Boolean, ForeignKey, UnicodeText, Integer, DateTime
from sqlalchemy.orm import relationship, aliased
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm.session import Session
import datetime
from elixir import *

Base = declarative_base()
__metadata__ = Base.metadata

class City(Base):
    __tablename__ = "City"
    name     = Column(Unicode(6), primary_key=True)
    rooms    = relationship("Room", backref="city")

    def __repr__(self):
        return u'<City "%s" with %d rooms>' % (self.name, len(self.rooms))

class Door(Base):
    __tablename__ = "Doors"

    locked = Column(Boolean)

    room_a_id = Column(Unicode(6), ForeignKey("Room.name"), nullable=False, primary_key=True)
    room_b_id = Column(Unicode(6), ForeignKey("Room.name"), nullable=False, primary_key=True)
    room_a = relationship("Room", primaryjoin="Door.room_a_id == Room.name")
    room_b = relationship("Room", primaryjoin="Door.room_b_id == Room.name")

    def __repr__(self):
        return u'<Door between %s %s%s>' % (self.room_a_id, self.room_b_id, ", locked" if self.locked and self.lockable() else (", open" if self.lockable() else ""))

    def __contains__(self, other):
        return other in [self.room_a, self.room_b, self.room_a_id, self.room_b_id]

    def lockable(self):
        return self.room_a.realm != self.room_b.realm

class Room(Base):
    __tablename__ = "Room"

    name      = Column(Unicode(6), primary_key=True)
    city_name = Column(Unicode(6), ForeignKey("City.name"), nullable=True)

    realm     = Column(Enum("V", "VV", "V'V", "CV", "CVV", "CV'V", "CVCCV", "CCVCV"))

    @property
    def doors(self):
        session = Session.object_session(self)
        Room2 = aliased(Room)
        return session.query(Room2)\
            .join(Room2.doorobjs, (Room, or_(Door.room_a_id == Room.name, Door.room_b_id == Room.name)))\
            .filter(Room2.name != Room.name)\
            .filter(Room.name == self.name)\
            .all()

    doorobjs  = relationship("Door",
                             primaryjoin=or_(name == Door.room_a_id, name == Door.room_b_id),
                             viewonly=True)

    def __repr__(self):
        return u'<Room "%s"%s %d doors>' % (self.name, 
                                            ' in city "%s"' % self.city.name if self.city is not None else "",
                                            len(self.doors))

    def doorTo(self, other):
        door = [door for door in self.doorobjs if other in door]
        if len(door) == 1:
            return door[0]
        else:
            print self, ".doorTo(", other, ")", self.doorobjs
            return None

class Selmaho(Base):
    """This class is used for letting game admins/BPFK members assign bonuses for selmaho"""
    __tablename__ = "selmaho"

    selmaho  = Column(Unicode(6), primary_key=True)
    multi    = Column(Float)
    words    = relationship("WordCard", backref="selmaho")

    def __repr__(self):
        return "<Selmaho '%s' multiplier %r>" % (self.selmaho, self.multi)

class WordCard(Base):
    __tablename__ = "wordcard"

    word       = Column(Unicode(6), primary_key=True)
    gloss      = Column(Unicode(32))
    definition = Column(UnicodeText)
    selmaho_name = Column(Unicode(6), ForeignKey("selmaho.selmaho"))
    rafsi      = Column(Unicode(13))
    rank       = Column(Integer)

    def __repr__(self):
        return '<Word "%s">' % (self.word)

class BagEntry(Base):
    __tablename__ = "bagentry"
    
    player_name = Column(Unicode(16), ForeignKey("player.username"), primary_key=True)
    player      = relationship("Player")
    word_word   = Column(Unicode(6), ForeignKey("wordcard.word"), primary_key=True)
    word        = relationship("WordCard")
    count       = Column(Integer)

class Player(Base):
    """This class represents a player as well as a session (one session per player)"""
    __tablename__ = "player"

    username  = Column(Unicode(16), primary_key=True)
    password  = Column(Unicode(40)) # sha1sum of the password
    
    join_date = Column(DateTime, default=datetime.datetime.now)

    status    = Column(Integer)
    login     = Column(DateTime)

    position_name = Column(Unicode(6), ForeignKey("Room.name"))
    position  = relationship(Room)
    
    health    = Column(Integer, default=1000)
    maxHealth = Column(Integer, default=1000)
    gold      = Column(Integer, default=0)
    fluency   = Column(Integer, default=1)
    cmavobag  = Column(Integer, default=100)
    gismubag  = Column(Integer, default=50)
    maxsenlen = Column(Integer, default=10)
    dexterity = Column(Integer, default=1)

    bag       = relationship(WordCard, secondary=BagEntry.__table__,
                             primaryjoin = username == BagEntry.player_name)

    def __repr__(self):
        return u'<Player "%s" (%sline) in room "%s">' % (self.username, u"On" if self.status == 1 else u"Off", self.position.name)

class Monster(Base):
    __tablename__ = "monster"
    
    id = Column(Integer, primary_key=True)

    name = Column(Unicode(32))

    health = Column(Integer, default = 100)

    position_name = Column(Unicode(6), ForeignKey("Room.name"))
    position = relationship(Room)

### things for the treasure chest game and combat

class HumanSentence(Base):
    __tablename__ = "humansentence"

    text     = Column(UnicodeText, primary_key=True)
    authorname = Column(Unicode(16), ForeignKey("player.username")) # if someone uses an "old" sentence, the damage will be halved and it will not be recorded again.
    author   = relationship(Player)
    score    = Column(Integer)
    reviews  = Column(Integer)

class WordFamiliarity(Base):
    __tablename__ = "wordfamiliarity"
    """This class records, wether or not a player has seen a word before."""
    player_name = Column(Unicode(16), ForeignKey("player.username"), primary_key=True)
    player = relationship(Player)
    word_word  = Column(Unicode(6), ForeignKey("wordcard.word"), primary_key=True)
    word = relationship(WordCard)
    count    = Column(Integer)
