from elixir import *
from sqlalchemy import MetaData

__metadata__ = MetaData()

class Player(Entity):
    """This class represents a player as well as a session (one session per player)"""
    username  = Field(Unicode(64), primary_key=True)
    password  = Field(Unicode(40)) # sha1sum of the password
    
    join_date = Field(DateTime, default=datetime.datetime.now)

    status    = Field(SmallInt)
    login     = Field(DateTime)

    position  = ForeignKey(Room, deferred="session")
    
    health    = Field(Integer, deferred="stats", default=1000)
    maxHealth = Field(Integer, deferred="stats", default=1000)
    gold      = Field(Integer, deferred="stats", default=0)
    fluency   = Field(Integer, deferred="stats", default=1)
    cmavobag  = Field(Integer, deferred="stats", default=100)
    gismubag  = Field(Integer, deferred="stats", default=50)
    maxsenlen = Field(Integer, deferred="stats", default=10)
    dexterity = Field(Integer, deferred="stats", default=1)

    

    def __repr__(self):
        return u'<Player "%s" (%sline)>' % (self.username, [u"On", u"Off"][self.status])

class Room(Entity):
    name     = Field(Unicode(6), primary_key=True)
    doors    = ManyToMany(Room)

### things for the treasure chest game and combat

class HumanSentence(Entity):
    text     = Field(UnicodeText, primary_key=True)
    author   = ForeignKey(Player) # if someone uses an "old" sentence, the damage will be halved and it will not be recorded again.
    score    = Field(Integer)
    reviews  = Field(Integer)

class Selmaho(Entity):
    """This class is used for letting game admins/BPFK members assign bonuses for selmaho"""
    selmaho  = Field(Unicode(12), primary_key=True)
    bonus    = Field(Float)

class WordCard(Entity):
    word       = Field(Unicode(6), primary_key=True)
    gloss      = Field(Unicode(32))
    definition = Field(UnicodeText)
    selmaho    = ForeignKey(Selmaho)

class WordFamiliarity(Entity):
    """This class records, wether or not a player has seen a word before."""
    player   = ForeignKey(Player)
    word     = ForeignKey(WordCard)
    count    = Field(Integer)
