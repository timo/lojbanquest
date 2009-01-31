from elixir import *
from sqlalchemy import MetaData

__metadata__ = MetaData()

class Player(Entity):
    """This class represents a player as well as a session (one session per player)"""
    username = Field(Unicode(64), primary_key=True)
    password = Field(Unicode(40)) # sha1sum of the password
    
    join_date = Field(DateTime, default=datetime.datetime.now)

    status   = Field(SmallInt)
    login    = Field(DateTime)

    position = ForeignKey(Room, deferred="session")
    


    def __repr__(self):
        return u'<Player "%s" (%sline)>' % (self.username, [u"On", u"Off"][self.status])

class Room(Entity):
    name     = Field(Unicode(6), primary_key=True)
    doors    = ManyToOne(Room)

class HumanSentence(Entity):
    text     = Field(UnicodeText, primary_key=True)
    authors  = ManyToMany(Player)
    score    = Field(Integer)
