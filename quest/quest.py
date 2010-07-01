from __future__ import with_statement

import os
from nagare import presentation, component, state, var
from nagare.namespaces import xhtml
import pkg_resources

from elixir import *

from webob.exc import HTTPOk

import models
import random

from subprocess import Popen, PIPE

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

    def enterRoom(self, roomname):
        player = session.query(models.Player).get(self.player)
        player.position = session.query(models.Room).get(roomname)

@presentation.render_for(GameSession)
def render(self, h, *args):
    h.head << h.head.title("LojbanQuest draft")
    if self.model() == "login":
        h << self.loginManager
    elif self.model() == "game":
        h << h.h1("Welcome to LojbanQuest!")
        h << self.playerBox
        h << self.playerBox.render(h, model="wordbag")
        h << self.roomDisplay
        h << h.div(self.roomDisplay.render(h, model="map"), style="position:absolute; right: 0; top: 0;")
    return h.root

class RoomDisplay(object):
    """This class encapsulates many Components that build up the GUI that
    the player uses to 'see' a room and status stuff."""
    def __init__(self, room, gs):
        self.gs = gs
        self.prev = room
        self.enterRoom(room)

    map_cache_path = lambda self, room, frm, typ: pkg_resources.resource_filename("quest", "../cache/%s_%s.%s" % (room, frm, typ))

    def create_map(self):
        img_path = self.map_cache_path(self.room, self.prev, "png")
        map_path = self.map_cache_path(self.room, self.prev, "map")

        thisroom = models.Room.query.filter_by(name=self.room).one()

        crawl = [thisroom]
        add = []
        for i in range(2):
            for room in crawl:
                for reached in room.doors:
                    if reached not in crawl and reached not in add:
                        add.append(reached)
            crawl.extend(add)
            add = []

        dotproc = Popen(["neato", "-Tpng", "-o" + img_path, "-Tcmapx_np", "-o" + map_path, "/dev/stdin"], stdin=PIPE)
        dotproc.stdin.write("""graph tersistuhas {
    graph [overlap=false]
    node [shape=none fontsize=10]
    edge [color=grey]
    subgraph cmavo {
        node [fontcolor=blue]\n""")

        for room in crawl:
            if len(room.name) != 5:
                if room in thisroom.doors:
                    dotproc.stdin.write("""        "%(name)s" [URL="goto/%(name)s"]\n""" % {"name": room.name})
                else:
                    dotproc.stdin.write("""        "%(name)s"\n""" % {"name": room.name})


        dotproc.stdin.write("""    } subgraph gismu {
        node[fontcolor=red]\n""")

        for room in crawl:
            if room.name == self.room:
                dotproc.stdin.write("""        "%(name)s" [shape=diamond]\n""" % {"name": room.name})
            elif room.name == self.prev:
                dotproc.stdin.write("""        "%(name)s" [shape=egg URL="goto/%(name)s"]\n""" % {"name": room.name})
            for other in room.doors:
                if other.name < room.name and other in crawl:
                    if room in thisroom.doors:
                        dotproc.stdin.write("""        "%(this)s" [URL="goto/%(this)s"]\n
            "%(this)s" -- "%(other)s"\n""" % {"this": room.name, "other": other.name})
                    else:
                        dotproc.stdin.write("""        "%(this)s" -- "%(other)s"\n""" % {"this": room.name, "other": other.name})
        
        dotproc.stdin.write("""    } }""")

        dotproc.stdin.close()

        dotproc.wait()

        return img_path, map_path

    def get_map_image(self):
        try:
            cached = open(self.map_cache_path(self.room, self.prev, "png"), "r")
            return cached.read()
        except IOError:
            pass

        (img_path, _) = self.create_map()

        imgdata = open(img_path, "r").read()

        return imgdata

    def get_map_map(self):
        try:
            cached = open(self.map_cache_path(self.room, self.prev, "map"), "r")
            return cached.read()
        except IOError:
            pass

        (_, map_path) = self.create_map()

        mapdata = open(map_path, "r").read()

        return mapdata

    def enterRoom(self, room):
        try:
            self.prev = self.room
        except:
            self.prev = room
        if isinstance(room, models.Room):
            #raise ProgrammingError("Do not call RoomDisplay.enterRoom with a Room instance.")
            self.room = room.name
        else:
            self.room = room
        
        self.monsters = component.Component(Monsters(self.gs))
        self.monsters.o.addMonster(component.Component(Monster(self.gs)))

        self.gs.enterRoom(self.room)

        print "entered room", self.room

@presentation.render_for(RoomDisplay)
def roomdisplay_render(self, h, binding, *args):
    room = models.Room.query.get(self.room)
    h << self.monsters
    if room.city:
        h << h.p("You are in ", h.span(room.name, id="roomname"), " in the city of ", h.span(room.city.name, id="cityname"))
    else:
        h << h.p("You are in ", h.span(room.name, id="roomname"))
    with h.div():
        h << "Doors:"
        with h.ul():
            h << (h.li(h.a(other.name).action(lambda other=other: self.enterRoom(other.name))) for other in room.doors if other.name != self.prev)
            h << h.li("Back: ", h.a(self.prev).action(lambda other=self.prev: self.enterRoom(self.prev)))

    return h.root

@presentation.render_for(RoomDisplay, model="map")
def render_map(self, h, binding, *args):
    h << h.img(usemap="tersistuhas").action(self.get_map_image)
    h << h.parse_htmlstring(self.get_map_map())
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
        np.position = models.Room.query.get(u"kalsa")
        session.add(np)
        session.flush()
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
