from __future__ import absolute_import

import re
from random import shuffle
from subprocess import Popen, PIPE

import pkg_resources
from nagare import presentation, component
from nagare.database import session
from sqlalchemy.sql.functions import random

from quest.exceptions import *
from quest.models import Room, WordCard
from quest.monster import *


class RoomDisplay(object):
    """This class encapsulates many Components that build up the GUI that
    the player uses to 'see' a room and status stuff."""
    def __init__(self, room, gs):
        self.gs = gs
        if isinstance(room, basestring):
            room = session.query(Room).get(room)
        self.prev = room
        self.room = room
        self.enterRoom(room)

    def map_cache_path(self, room, frm, typ):
        """generate a path for a cache image from the current room, where we come frm and what typ of file we want (alternatively put %s in typ)"""
        
        # scan for lockable doors from the room we are currently in
        locks = "_"

        doors = session.query(Room).get(room).doorobjs
        for door in doors:
            locks += "l" if door.locked else "o" if door.lockable() else ""

        if locks == "_": locks = ""

        return pkg_resources.resource_filename("quest", "../cache/%s_%s%s.%s" % (room, frm.name, locks, typ))

    def crawl_for_map(self, start):
        crawl = [start]
        add = []
        for i in range(2 if len(start.name) == 5 else 1):
            for room in crawl:
                for reached in room.doors:
                    if reached not in crawl and reached not in add:
                        add.append(reached)
            crawl.extend(add)
            add = []

        return crawl

    def create_map(self):
        path = self.map_cache_path(self.room.name, self.prev, "%s")
        img_path = path % ("png")
        map_path = path % ("map")
        dot_path = path % ("dot")

        crawl = self.crawl_for_map(self.room)

        dotproc = Popen(["neato", "-Tpng", "-o" + img_path, "-Tcmapx_np", "-o" + map_path, "-Tcanon", "-o", dot_path,  "/dev/stdin"], stdin=PIPE)
        #dotproc = Popen(["cat"], stdin=PIPE)
        dotproc.stdin.write("""graph tersistuhas {
    graph [overlap=false bgcolor="transparent" model=circuit]
    node [shape=none fontsize=7]
    edge [color=grey]
    subgraph cmavo {
        node [fontcolor=blue]\n""")

        for room in crawl:
            if len(room.name) != 5:
                if room in self.room.doors:
                    dotproc.stdin.write("""        "%(name)s" [fontsize=10 URL="goto/%(name)s"]\n""" % {"name": room.name})
                else:
                    dotproc.stdin.write("""        "%(name)s"\n""" % {"name": room.name})


        dotproc.stdin.write("""    } subgraph gismu {
        node[fontcolor=red]\n""")

        for room in self.room.doors:
            dotproc.stdin.write("""        "%(this)s" [fontsize=10 URL="goto/%(this)s"]\n""" % {"this": room.name})


        for room in crawl:
            if room == self.room:
                dotproc.stdin.write("""        "%(name)s" [shape=diamond fontsize=12 pos="0.0,0.0"]\n""" % {"name": room.name})
            elif room.name == self.prev.name:
                dotproc.stdin.write("""        "%(name)s" [shape=octagon color=grey fontsize=10 URL="goto/%(name)s" pos="0.0,-0.001"]\n""" % {"name": room.name})
            
            for other in room.doors:
                if other.name < room.name and other in crawl:
                    if other.realm != room.realm and (other == self.room or room == self.room): # only show doors next to the room we're in.
                        door = room.doorTo(other)
                        if door and door.locked:
                            arrow = "box"
                        else:
                            arrow = "obox"
                    else:
                        arrow = ""
                    headtail = " "
                    if other.city != room.city:
                        arrow += "inv"
                        if other.city is not None:
                            headtail += 'arrowhead="%s" ' % arrow
                        if room.city is not None:
                            headtail += 'arrowtail="%s" ' % arrow
                        if room.city is not None and other.city is not None:
                            headtail += 'dir="both" '
                        elif room.city is not None:
                            headtail += 'dir="back"'
                        else:
                            headtail += 'dir="forward"'
                    else:
                        if arrow != "":
                            headtail = 'dir="forward" arrowhead="%s"' % (arrow)
                    if headtail != "":
                        headtail = "[" + headtail + "]"
                    dotproc.stdin.write("""        "%(this)s" -- "%(other)s" %(ht)s\n""" % {"this": room.name, "other": other.name, "ht": headtail})
        
        dotproc.stdin.write("""    } }""")

        dotproc.stdin.close()

        dotproc.wait()

        return img_path, map_path


    def get_map_image(self):
        try:
            cached = open(self.map_cache_path(self.room.name, self.prev, "png"), "r")
            return cached.read()
        except IOError:
            pass

        (img_path, _) = self.create_map()

        imgdata = open(img_path, "r").read()

        return imgdata


    def get_map_map(self):
        try:
            cached = open(self.map_cache_path(self.room.name, self.prev, "map"), "r")
            return cached.read()
        except IOError:
            pass

        (_, map_path) = self.create_map()

        mapdata = open(map_path, "r").read()

        return mapdata

    def enterRoom(self, room, binding = None):
        try:
            prevroom = self.room
        except:
            prevroom = room
        if isinstance(room, Room):
            nextroom = room
        else:
            nextroom = session.query(Room).get(room)
        
        try:
            self.gs.enterRoom(nextroom)
        except DoorLockedException, e:
            success = binding.call(UnlockChallenge())
            if success:
                print "yay"
                self.gs.enterRoom(nextroom, force=True)
            else:
                print "nay :("
                return
        
        self.room = nextroom
        self.prev = prevroom

        # TODO: just update the previous monsters component instead.
        self.monsters = component.Component(Monsters(self.gs))
        self.monsters.o.addMonster(component.Component(Monster(self.gs)))

class UnlockChallenge(object):
    def __init__(self):
        # select a few random words from the word cards
        words = session.query(WordCard).order_by(random()).limit(6).all()

        self.correct = words[0]
        self.wrongs = words[1:]

        self.words = words
        shuffle(self.words)

    def choose(self, word):
        if word == self.correct:
            return True
        elif word in self.wrongs:
            return False
        else:
            raise Exception("Word neither wrong nor correct. wtf?")

@presentation.render_for(RoomDisplay)
def roomdisplay_render(self, h, binding, *args):
    def door(from_, to):
        dooro = from_.doorTo(to)
        if dooro:
            return h.span(h.a(to.name).action(lambda other=to: self.enterRoom(other, binding)), "(locked)" if dooro.locked else "(unlocked)" if dooro.lockable() else "")
        return h.span(h.a(to.name).action(lambda other=to: self.enterRoom(other, binding)), "error! couldn't find a door object. wtf?")

    try:
        h << self.monsters
    except AttributeError:
        pass
    if self.room.city:
        h << h.p("You are in ", h.span(self.room.name, id="roomname"), " in the city of ", h.span(self.room.city.name, id="cityname"))
    else:
        h << h.p("You are in ", h.span(self.room.name, id="roomname"))
    with h.div():
        h << "Doors:"
        with h.ul():
            h << (h.li(door(self.room, other)) for other in self.room.doors if other != self.prev)
            if self.room != self.prev:
                h << h.li("Back: ", door(self.room, self.prev))

    with h.ul(id="players"):
        for player in self.room.players:
            h << h.li(player.username, id="player_" + player.username)

    return h.root

gotorex = re.compile("goto/([^\"]+)")

@presentation.render_for(RoomDisplay, model="map")
def render_map(self, h, binding, *args):
    h << h.img(usemap="#tersistuhas").action(self.get_map_image)

    mapstr = self.get_map_map()

    mapobj = h.parse_htmlstring(mapstr, fragment=True)[0]

    for area in mapobj.xpath("//area"):
        roomname = unicode(area.get("href").split("/")[1].replace("&#39;", "'"))
        area.action(lambda other=roomname: self.enterRoom(other, binding))

    h << mapobj
    return h.root

@presentation.render_for(UnlockChallenge)
def render_challenge(self, h, binding, *args):
    with h.div():
        h << h.span("What's the word for ", self.correct.gloss, "?")
        with h.ul():
            for word in self.words:
                h << h.li(h.a(word.word).action(lambda word=word: binding.answer(self.choose(word))))

    return h.root

@presentation.render_for(UnlockChallenge, model="map")
def render_challenge_with_map(self, h, binding, *args):
    return h.root
