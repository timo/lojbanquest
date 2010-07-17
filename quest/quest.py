from __future__ import with_statement, absolute_import

from nagare import presentation, component, state, var
from nagare.namespaces import xhtml
from nagare.database import session

from quest.models import Player as PlayerModel, Room, WordCard, BagEntry
from quest.exceptions import *
from quest.eventlog import Log, send_to
import random

# gather models
from quest.roomdisplay import RoomDisplay
from quest.monster import Monster, Monsters
from quest.questlogin import QuestLogin

class GameSession(object):
    def __init__(self):
        self.loginManager = component.Component(QuestLogin())
        self.loginManager.on_answer(self.startGame)
        self.model = state.stateless(var.Var("login"))

    def startGame(self, player):
        self.player =  session.query(PlayerModel).get(player)

        self.playerBox = component.Component(Player(self.player, self))
        self.roomDisplay = component.Component(RoomDisplay(self.player.position, self))
        self.spellInput = component.Component(SpellInput(self))

        self.eventlog = component.Component(Log(self))

        self.model("game")

        del self.loginManager

    def enterRoom(self, room, force = False):
        oldpos = self.player.position

        if isinstance(room, Room):
            newposition = room
        else:
            newposition = session.query(Room).get(room)
        
        # when we start the game, we have no old position.
        if oldpos == newposition:
            print "ignoring GameSession.enterRoom."
            send_to(self.player.position, "%s entered" % (self.player.username))
            return

        # find the door object. if it's locked, don't let us through, if it's lockable, shut it behind us.
        door = oldpos.doorTo(newposition)

        if door.locked and door.lockable():
            if force:
                door.locked = False # unlock it so that one person can get through behind us
            else:
                raise DoorLockedException
        if door.lockable() and not force:
            door.locked = True # TODO: delay this by a few seconds, so that party members can come along?

        send_to(self.player.position, "%s left" % (self.player.username))
        self.player.position = newposition
        send_to(self.player.position, "%s entered" % (self.player.username))

class Wordbag(object):
    """This class holds the words that the player posesses."""
    def __init__(self, gs):
        self.gs = gs

        self.getWords()

    def getWords(self):
        entries = session.query(BagEntry).filter(BagEntry.player == self.gs.player).all()
        self.words = dict([(entry.word, entry.count) for entry in entries])

class SpellInput(object):
    def __init__(self, gs):
        self.gs = gs
        self.text = var.Var()
        self.errorcards = []

    def cast(self, text, target=None):
        self.text(text)
        words = self.text().split()

        cards = [session.query(WordCard).get(word) for word in words]

        # make a tally for our cards so we can check if we have enough
        cdict = {}
        for card in cards:
            if card in cdict:
                cdict[card] += 1
            else:
                cdict[card] = 1

        errorcards = []

        for card, count in cdict.iteritems():
            entry = session.query(BagEntry.count).get((self.gs.player.username, card.word))
            if not entry:
                errorcards.append(card.word)
            elif entry.count < count:
                errorcards.append(card.word)

        if errorcards:
            self.errorcards = errorcards
            return

        for card, count in cdict.iteritems():
            entry = session.query(BagEntry).get((self.gs.player.username, card.word))
            entry.count -= count
            print entry.word.word, " now has count ", entry.count
            if entry.count <= 0:
                session.delete(entry)

        # update wordbag display
        self.gs.playerBox.o.wordbag.getWords()

        print ["<%s %r>" % (word.word, word.rank) for word in cards]
        score = reduce(lambda scr, wrd: scr + wrd.rank, cards, 0)
        print score
        
        self.text("")

@presentation.render_for(SpellInput)
def render_spellinput(self, h, binding, *args):
    if self.errorcards:
        textwords = self.text().split()
        h << h.span(*[h.span(word, style="color: red") if word in self.errorcards else h.span(word) for word in textwords])
    with h.form():
        h << h.input().action(self.cast)

    return h.root

class Player(object):
    """This Component represents the player of the game."""
    def __init__(self, player, gs):
        self.o = player
        self.wordbag = state.stateless(Wordbag(gs))

@presentation.render_for(Player)
def player_render(self, h, binding, *args):
    with h.div(class_ = "playerbox"):
        h << h.h1(self.o.username)
        with h.span():
           h << "You currently have "
           h << h.span(self.o.health, id="hp")
           h << " health points."

    return h.root

@presentation.render_for(Player, model="wordbag")
def wordbag_render(self, h, binding, *args):
    if len(self.wordbag.words) > 0:
        with h.div(class_="wordbag"):
            h << {"style": "column-count:5; -moz-column-count:5; -webkit-column-count:5; position:absolute; bottom: 5px; left: 5px; right: 5px; height: auto" }
            with h.ul():
                for wo, ct in self.wordbag.words.iteritems():
                    with h.li():
                        h << h.span(ct, class_="count")
                        h << h.a(" " + wo.word)
    else:
        with h.div(class_="wordbag"):
            h << "Woops. No words :("
    
    return h.root


@presentation.render_for(GameSession)
def render(self, h, *args):
    h.head << h.head.title("LojbanQuest draft")
    if self.model() == "login":
        h << self.loginManager
    elif self.model() == "game":
        h << h.h1("Welcome to LojbanQuest!")
        h << self.playerBox
        h << self.playerBox.render(xhtml.AsyncRenderer(h), model="wordbag")
        h << self.spellInput.render(h)
        h << self.roomDisplay
        h << self.eventlog
        h << h.div(self.roomDisplay.render(h, model="map"), style="position:absolute; right: 0; top: 0;")
    return h.root


# ---------------------------------------------------------------

app = GameSession
