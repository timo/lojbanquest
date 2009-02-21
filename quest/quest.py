from __future__ import with_statement

import os
from nagare import presentation, component, state, var
from nagare.namespaces import xhtml

from elixir import *

import models
import random

class GameSession(object):
    def __init__(self):
        self.loginManager = component.Component(QuestLogin())
        self.loginManager.on_answer(self.startGame)
        self.model = state.stateless(var.Var("login"))

    def startGame(self, player):
        plo = models.Player.get(player)
        self.player = player

        self.playerBox = component.Component(Player(player, self))
        self.roomDisplay = component.Component(RoomDisplay(plo.position.name, self))

        self.model("game")

@presentation.render_for(GameSession)
def render(self, h, *args):
    h.head << h.head.title("LojbanQuest draft")
    if self.model() == "login":
        h << self.loginManager
    elif self.model() == "game":
        h << h.h1("Welcome to LojbanQuest!")
        h << self.playerBox.render(xhtml.AsyncRenderer(h))
        h << self.playerBox.render(xhtml.AsyncRenderer(h), model="wordbag")
        h << self.roomDisplay
    return h.root

class RoomDisplay(object):
    """This class encapsulates many Components that build up the GUI that
    the player uses to 'see' a room and status stuff."""
    def __init__(self, room, gs):
        self.gs = gs
        self.enterRoom(room)

    def enterRoom(self, room):
        if isinstance(room, models.Room):
            raise ProgrammingError("Do not call RoomDisplay.enterRoom with a Room instance.")
            self.room = room.name
        else:
            self.room = room

        self.monsters = component.Component(Monsters(self.gs))
        self.monsters.o.addMonster(component.Component(Monster(self.gs)))

@presentation.render_for(RoomDisplay)
def roomdisplay_render(self, h, binding, *args):
    room = models.Room.query.get(self.room)
    h << h.p("You are in ", h.span(room.name, id="roomname"))
    h << self.monsters
    with h.div():
        h << "Doors:"
        with h.ul():
            h << (h.li(other.name) for other in room.doors)

    return h.root

class Monster(object):
    def __init__(self, gs):
        self.hp = 100
        self.name = "Slime of Vagueness"

@presentation.render_for(Monster)
def monster_render(self, h, binding, *args):
    with h.div(class_="monster"):
        h << self.name
        h << h.br()
        h << h.span("%i hp" % self.hp, class_="hp")
    return h.root

class Monsters(object):
    """This Component holds all Monsters in the room and allows the player
    to select a Monster to attack."""
    def __init__(self, gs):
        self.monsters = []

    def addMonster(self, monster):
        self.monsters.append(monster)

@presentation.render_for(Monsters)
def monsters_render(self, h, binding, *args):
    for mon in self.monsters:
        h << mon

    return h.root

class Wordbag(object):
    """This class holds the words that the player posesses."""
    def __init__(self, gs):
        self.diceWords()

    def diceWords(self):
        self.words = {}

        words = list(models.WordCard.query.order_by(models.WordCard.word))
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

class Player(object):
    """This Component represents the player of the game."""
    def __init__(self, name, gs):
        self.name = name
        self.hp = 100
        self.wordbag = state.stateless(Wordbag(gs))

    def changeHp(self, offset):
        self.hp += offset

@presentation.render_for(Player)
def player_render(self, h, binding, *args):
    with h.div(class_ = "playerbox"):
        h << h.h1(self.name)
        with h.span():
           h << "You currently have "
           h << h.span(self.hp, id="hp")
           h << " health points."
           h << h.a("--").action(lambda: self.changeHp(-1))
           h << h.a("++").action(lambda: self.changeHp(+1))

    return h.root

@presentation.render_for(Player, model="wordbag")
def wordbag_render(self, h, binding, *args):
    if len(self.wordbag.words) > 0:
        with h.div(class_="wordbag"):
            h << {"style": "-moz-column-count:5;" }
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

class QuestLogin(object):
    def __init__(self):
        self.message = state.stateless(var.Var(""))

    def login(self, username, password, binding):
        po = models.Player.query.get(username())
        if not po:
            self.message("No such user. Try registering instead.")
        elif po.password != password():
            self.message("Login failed.")
        else:
            binding.answer(username())
         

    def register(self, username, password, binding):
        # see if there are duplicate players.
        if models.Player.query.get(username()):
            self.message("A player with that username already exists.")
            return

        np = models.Player(username = username(), password = password())
        np.position = models.Room.query.get("kalsa")
        session.add(np)
        self.login(username, password, binding)


@presentation.render_for(QuestLogin)
def login_form(self, h, binding, *args):
    un = var.Var()
    pwd = var.Var()
    return h.form("Please sign in with your username and password or register a new account.",
                  h.br(),
                  self.message(),
                  h.br(),
                  h.input.action(un),
                  h.input.action(pwd),
                  h.input(type="submit", value="login").action(lambda: self.login(un, pwd, binding)),
                  h.input(type="submit", value="register").action(lambda: self.register(un, pwd, binding))
                  )

# ---------------------------------------------------------------

app = GameSession
