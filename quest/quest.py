from __future__ import with_statement, absolute_import

from nagare import presentation, component, state, var
from nagare.namespaces import xhtml
from nagare.database import session

from quest.models import Player as PlayerModel, Room, WordCard 
import random

# gather models
from quest.roomdisplay import RoomDisplay
from quest.monster import Monster, Monsters
from quest.questlogin import QuestLogin

class DoorLockedException(Exception): pass

class GameSession(object):
    def __init__(self):
        self.loginManager = component.Component(QuestLogin())
        self.loginManager.on_answer(self.startGame)
        self.model = state.stateless(var.Var("login"))

    def startGame(self, player):
        self.player =  session.query(PlayerModel).get(player)

        self.playerBox = component.Component(Player(self.player, self))
        self.roomDisplay = component.Component(RoomDisplay(self.player.position, self))

        self.model("game")

    def enterRoom(self, room, force = False):
        oldpos = self.player.position

        if isinstance(room, Room):
            newposition = room
        else:
            newposition = session.query(Room).get(room)
        
        # when we start the game, we have no old position.
        if oldpos == newposition:
            print "ignoring GameSession.enterRoom."
            return

        # find the door object. if it's locked, don't let us through, if it's lockable, shut it behind us.
        door = oldpos.doorTo(newposition)

        if door.locked and door.lockable() and not force:
            raise DoorLockedException
        if door.lockable() and not force:
            door.locked = True # TODO: delay this by a few seconds, so that party members can come along?

        self.player.position = newposition

class Wordbag(object):
    """This class holds the words that the player posesses."""
    def __init__(self, gs):
        self.diceWords()

    def diceWords(self):
        self.words = {}

        words = list(session.query(WordCard).order_by(WordCard.word).all())
        sum = 0
        while sum < 100:
            num = random.randint(1, 10)
            self.words[random.choice(words)] = num
            sum += num

    def useWord(self, wo):
        wc = [wrd for wrd in self.words if wrd.word == wo][0]
        self.words[wc] -= 1
        if self.words[wc] == 0:
            del self.words[wc]

class SpellInput(object):
    def __init__(self, gs):
        self.gs = gs
        self.text = var.Var()

    def validate(self):
        pass

class Player(object):
    """This Component represents the player of the game."""
    def __init__(self, player, gs):
        self.o = player
        self.wordbag = state.stateless(Wordbag(gs))

    def changeHp(self, offset):
        self.o.hp += offset

@presentation.render_for(Player)
def player_render(self, h, binding, *args):
    with h.div(class_ = "playerbox"):
        h << h.h1(self.o.username)
        with h.span():
           h << "You currently have "
           h << h.span(self.o.health, id="hp")
           h << " health points."
           h << h.a("--").action(lambda: self.changeHp(-1))
           h << h.a("++").action(lambda: self.changeHp(+1))

    return h.root

@presentation.render_for(Player, model="wordbag")
def wordbag_render(self, h, binding, *args):
    if len(self.wordbag.words) > 0:
        with h.div(class_="wordbag"):
            h << {"style": "column-count:5; -moz-column-count:5; -webkit-column-count:5; position:absolute; bottom: 5px; left: 5px; right: 5px; height: auto" }
            h << h.a("re-fill bag.").action(self.wordbag.diceWords)
            with h.ul():
                for wo, ct in self.wordbag.words.iteritems():
                    with h.li():
                        h << h.span(ct, class_="count")
                        h << h.a(" " + wo.word).action(lambda wo=wo: self.wordbag.useWord(wo.word))
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
        h << self.roomDisplay
        h << h.div(self.roomDisplay.render(h, model="map"), style="position:absolute; right: 0; top: 0;")
    return h.root


# ---------------------------------------------------------------

app = GameSession
