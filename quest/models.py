from elixir import *
from sqlalchemy import MetaData
import datetime

__metadata__ = MetaData()

class City(Entity):
    rooms    = OneToMany("Room")
    name     = Field(Unicode(6), primary_key=True)

class Room(Entity):
    name     = Field(Unicode(6), primary_key=True)
    doors    = ManyToMany("Room")
    city     = ManyToOne("City")

class Player(Entity):
    """This class represents a player as well as a session (one session per player)"""
    username  = Field(Unicode(64), primary_key=True)
    password  = Field(Unicode(40)) # sha1sum of the password
    
    join_date = Field(DateTime, default=datetime.datetime.now)

    status    = Field(Integer)
    login     = Field(DateTime)

    position  = ManyToOne(Room)
    
    health    = Field(Integer, default=1000)
    maxHealth = Field(Integer, default=1000)
    gold      = Field(Integer, default=0)
    fluency   = Field(Integer, default=1)
    cmavobag  = Field(Integer, default=100)
    gismubag  = Field(Integer, default=50)
    maxsenlen = Field(Integer, default=10)
    dexterity = Field(Integer, default=1)

    def __repr__(self):
        return u'<Player "%s" (%sline)>' % (self.username, [u"On", u"Off"][self.status])

class Monster(Entity):
    name = Field(Unicode(64))

    health = Field(Integer, default = 100)

    position = ManyToOne(Room)

### things for the treasure chest game and combat

class HumanSentence(Entity):
    text     = Field(UnicodeText, primary_key=True)
    author   = ManyToOne(Player) # if someone uses an "old" sentence, the damage will be halved and it will not be recorded again.
    score    = Field(Integer)
    reviews  = Field(Integer)

class Selmaho(Entity):
    """This class is used for letting game admins/BPFK members assign bonuses for selmaho"""
    selmaho  = Field(Unicode(6), primary_key=True)
    multi    = Field(Float)

    def __repr__(self):
        return "<Selmaho '%s' multiplier %f>" % (self.selmaho, self.multi)

class WordCard(Entity):
    word       = Field(Unicode(6), primary_key=True)
    gloss      = Field(Unicode(32))
    definition = Field(UnicodeText)
    selmaho    = ManyToOne(Selmaho)
    rafsi      = Field(Unicode(13))

class WordFamiliarity(Entity):
    """This class records, wether or not a player has seen a word before."""
    player   = ManyToOne(Player)
    word     = ManyToOne(WordCard)
    count    = Field(Integer)
